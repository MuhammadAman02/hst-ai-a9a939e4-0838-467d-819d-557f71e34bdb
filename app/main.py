from nicegui import ui, app
import os
from pathlib import Path
import tempfile
import uuid
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image
import io
import base64
from skimage import color, exposure

from app.services.skin_tone import (
    detect_skin_tone,
    get_color_recommendations,
    adjust_skin_tone,
    SKIN_TONE_CATEGORIES
)

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Store user sessions
user_data: Dict[str, Dict] = {}

@ui.page('/')
def index():
    """Main application page for skin tone color advisor."""
    
    # Initialize session data if not exists
    session_id = app.storage.user.get('session_id', None)
    if not session_id:
        session_id = str(uuid.uuid4())
        app.storage.user['session_id'] = session_id
        user_data[session_id] = {
            'image_path': None,
            'original_image': None,
            'skin_tone': None,
            'recommended_colors': None,
            'adjusted_image': None
        }
    
    with ui.card().classes('w-full max-w-5xl mx-auto'):
        ui.label('Skin Tone Color Advisor').classes('text-2xl font-bold text-center')
        ui.label('Upload a photo to get personalized color recommendations based on skin tone').classes('text-center mb-4')
    
    with ui.card().classes('w-full max-w-5xl mx-auto mt-4'):
        with ui.row().classes('w-full items-center justify-center'):
            ui.upload(
                label='Upload Image',
                auto_upload=True,
                on_upload=lambda e: handle_upload(e, session_id)
            ).props('accept=".jpg, .jpeg, .png"').classes('max-w-xs')
    
    # Container for the image and color recommendations
    with ui.row().classes('w-full max-w-5xl mx-auto mt-4 gap-4'):
        # Left column for image
        with ui.card().classes('flex-1'):
            image_container = ui.element('div').classes('w-full flex justify-center')
            
            # This will be populated after image upload
            @ui.refreshable
            def display_image():
                if user_data[session_id]['image_path']:
                    # Display the current image (original or adjusted)
                    current_image = user_data[session_id].get('adjusted_image') or user_data[session_id]['original_image']
                    if current_image is not None:
                        img_bytes = io.BytesIO()
                        current_image.save(img_bytes, format='PNG')
                        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
                        ui.image(f"data:image/png;base64,{img_base64}").classes('max-w-full max-h-80 object-contain')
                    else:
                        ui.label('Error loading image').classes('text-red-500')
                else:
                    ui.label('No image uploaded').classes('text-gray-500')
            
            display_image()
            
        # Right column for skin tone and color recommendations
        with ui.card().classes('flex-1'):
            ui.label('Skin Tone Analysis').classes('text-xl font-bold')
            
            @ui.refreshable
            def display_skin_tone():
                if user_data[session_id].get('skin_tone'):
                    ui.label(f"Detected Skin Tone: {user_data[session_id]['skin_tone']}").classes('font-bold mt-2')
                    
                    # Skin tone adjustment slider
                    ui.label('Adjust Skin Tone:').classes('mt-4')
                    with ui.row().classes('items-center w-full'):
                        ui.select(
                            options=SKIN_TONE_CATEGORIES,
                            value=user_data[session_id]['skin_tone'],
                            on_change=lambda e: adjust_image_skin_tone(e.value, session_id)
                        ).classes('w-full')
                    
                    # Display recommended colors
                    if user_data[session_id].get('recommended_colors'):
                        ui.label('Recommended Colors:').classes('font-bold mt-4')
                        with ui.row().classes('flex-wrap gap-2 mt-2'):
                            for color_hex in user_data[session_id]['recommended_colors']:
                                with ui.card().classes('p-2'):
                                    ui.element('div').classes(f'w-16 h-16 rounded').style(f'background-color: {color_hex}')
                                    ui.label(color_hex).classes('text-center text-sm mt-1')
                else:
                    ui.label('Upload an image to see skin tone analysis').classes('text-gray-500')
            
            display_skin_tone()
    
    # Footer with information
    with ui.card().classes('w-full max-w-5xl mx-auto mt-4'):
        ui.label('How it works:').classes('font-bold')
        with ui.row().classes('gap-2'):
            with ui.card().classes('flex-1 p-3'):
                ui.label('1. Upload a photo').classes('font-bold')
                ui.label('Upload a clear photo showing the person\'s face or skin')
            with ui.card().classes('flex-1 p-3'):
                ui.label('2. Analyze skin tone').classes('font-bold')
                ui.label('The app detects the dominant skin tone in the image')
            with ui.card().classes('flex-1 p-3'):
                ui.label('3. Get recommendations').classes('font-bold')
                ui.label('See color palettes that complement the detected skin tone')
            with ui.card().classes('flex-1 p-3'):
                ui.label('4. Try different tones').classes('font-bold')
                ui.label('Adjust the skin tone to see how different colors would look')

    async def handle_upload(event, session_id: str):
        """Process the uploaded image."""
        try:
            # Save uploaded file
            for file_info in event.files:
                ext = Path(file_info.name).suffix
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir=UPLOAD_DIR)
                file_path = temp_file.name
                
                with open(file_path, 'wb') as f:
                    f.write(await file_info.read())
                
                # Process the image
                try:
                    # Open and process the image
                    img = Image.open(file_path).convert('RGB')
                    
                    # Resize if too large for processing
                    max_size = 1000
                    if max(img.size) > max_size:
                        ratio = max_size / max(img.size)
                        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                        img = img.resize(new_size, Image.LANCZOS)
                    
                    # Store the image and path
                    user_data[session_id]['image_path'] = file_path
                    user_data[session_id]['original_image'] = img
                    
                    # Detect skin tone
                    skin_tone = detect_skin_tone(np.array(img))
                    user_data[session_id]['skin_tone'] = skin_tone
                    
                    # Get color recommendations
                    recommended_colors = get_color_recommendations(skin_tone)
                    user_data[session_id]['recommended_colors'] = recommended_colors
                    
                    # Clear any previously adjusted image
                    user_data[session_id]['adjusted_image'] = None
                    
                    # Refresh the UI components
                    display_image.refresh()
                    display_skin_tone.refresh()
                    
                except Exception as e:
                    ui.notify(f"Error processing image: {str(e)}", type='negative')
                    print(f"Error processing image: {str(e)}")
                
                break  # Process only the first file if multiple are uploaded
        except Exception as e:
            ui.notify(f"Upload failed: {str(e)}", type='negative')
            print(f"Upload failed: {str(e)}")

    def adjust_image_skin_tone(new_tone: str, session_id: str):
        """Adjust the skin tone of the image."""
        try:
            if user_data[session_id]['original_image'] is None:
                return
            
            # Adjust the skin tone
            original_img_array = np.array(user_data[session_id]['original_image'])
            adjusted_img_array = adjust_skin_tone(original_img_array, new_tone)
            
            # Convert back to PIL Image
            adjusted_img = Image.fromarray(adjusted_img_array.astype('uint8'))
            user_data[session_id]['adjusted_image'] = adjusted_img
            
            # Update skin tone and color recommendations
            user_data[session_id]['skin_tone'] = new_tone
            user_data[session_id]['recommended_colors'] = get_color_recommendations(new_tone)
            
            # Refresh the UI
            display_image.refresh()
            display_skin_tone.refresh()
            
        except Exception as e:
            ui.notify(f"Error adjusting skin tone: {str(e)}", type='negative')
            print(f"Error adjusting skin tone: {str(e)}")