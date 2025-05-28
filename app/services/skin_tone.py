"""
Skin tone detection and color recommendation service.
"""
from typing import Dict, List, Tuple
import numpy as np
from skimage import color, exposure
from PIL import Image

# Define skin tone categories
SKIN_TONE_CATEGORIES = [
    "Fair",
    "Light",
    "Medium",
    "Olive",
    "Tan",
    "Deep",
    "Dark"
]

# Color recommendations for each skin tone
COLOR_RECOMMENDATIONS: Dict[str, List[str]] = {
    "Fair": [
        "#E6B3B3",  # Soft pink
        "#D1E6B3",  # Soft lime
        "#B3E6CC",  # Mint
        "#B3CCE6",  # Baby blue
        "#D1B3E6",  # Lavender
        "#800000",  # Burgundy
        "#008080",  # Teal
    ],
    "Light": [
        "#FFB6C1",  # Light pink
        "#98FB98",  # Pale green
        "#ADD8E6",  # Light blue
        "#DDA0DD",  # Plum
        "#F08080",  # Coral
        "#4682B4",  # Steel blue
        "#556B2F",  # Olive green
    ],
    "Medium": [
        "#FF6347",  # Tomato
        "#6B8E23",  # Olive drab
        "#4169E1",  # Royal blue
        "#BA55D3",  # Medium orchid
        "#20B2AA",  # Light sea green
        "#CD5C5C",  # Indian red
        "#DAA520",  # Goldenrod
    ],
    "Olive": [
        "#FF4500",  # Orange red
        "#2E8B57",  # Sea green
        "#9932CC",  # Dark orchid
        "#8B4513",  # Saddle brown
        "#008B8B",  # Dark cyan
        "#B8860B",  # Dark goldenrod
        "#C71585",  # Medium violet red
    ],
    "Tan": [
        "#FF8C00",  # Dark orange
        "#006400",  # Dark green
        "#8B008B",  # Dark magenta
        "#E9967A",  # Dark salmon
        "#8FBC8F",  # Dark sea green
        "#483D8B",  # Dark slate blue
        "#B22222",  # Firebrick
    ],
    "Deep": [
        "#FFA500",  # Orange
        "#00FF00",  # Lime
        "#FF00FF",  # Magenta
        "#00FFFF",  # Cyan
        "#FFFF00",  # Yellow
        "#800080",  # Purple
        "#DC143C",  # Crimson
    ],
    "Dark": [
        "#FFD700",  # Gold
        "#7CFC00",  # Lawn green
        "#FF1493",  # Deep pink
        "#00BFFF",  # Deep sky blue
        "#F0E68C",  # Khaki
        "#ADFF2F",  # Green yellow
        "#FF69B4",  # Hot pink
    ]
}

def detect_skin_tone(image: np.ndarray) -> str:
    """
    Detect the dominant skin tone in an image.
    
    Args:
        image: RGB image as numpy array
        
    Returns:
        String representing the detected skin tone category
    """
    try:
        # Convert to LAB color space (better for skin detection)
        lab_image = color.rgb2lab(image)
        
        # Simple skin detection based on color ranges in LAB space
        # These thresholds are approximate and can be refined
        l_range = (50, 80)  # Lightness
        a_range = (5, 30)   # Green-Red
        b_range = (10, 40)  # Blue-Yellow
        
        # Create a mask for likely skin pixels
        skin_mask = (
            (lab_image[:,:,0] >= l_range[0]) & (lab_image[:,:,0] <= l_range[1]) &
            (lab_image[:,:,1] >= a_range[0]) & (lab_image[:,:,1] <= a_range[1]) &
            (lab_image[:,:,2] >= b_range[0]) & (lab_image[:,:,2] <= b_range[1])
        )
        
        # If no skin detected, use a more lenient approach
        if np.sum(skin_mask) < 100:
            l_range = (30, 90)
            a_range = (0, 35)
            b_range = (5, 45)
            
            skin_mask = (
                (lab_image[:,:,0] >= l_range[0]) & (lab_image[:,:,0] <= l_range[1]) &
                (lab_image[:,:,1] >= a_range[0]) & (lab_image[:,:,1] <= a_range[1]) &
                (lab_image[:,:,2] >= b_range[0]) & (lab_image[:,:,2] <= b_range[1])
            )
        
        # If still no significant skin detected, return a default
        if np.sum(skin_mask) < 100:
            return "Medium"
        
        # Get the average L value (lightness) of skin pixels
        skin_l_values = lab_image[:,:,0][skin_mask]
        avg_lightness = np.mean(skin_l_values)
        
        # Classify based on lightness
        if avg_lightness >= 75:
            return "Fair"
        elif avg_lightness >= 70:
            return "Light"
        elif avg_lightness >= 65:
            return "Medium"
        elif avg_lightness >= 60:
            return "Olive"
        elif avg_lightness >= 55:
            return "Tan"
        elif avg_lightness >= 50:
            return "Deep"
        else:
            return "Dark"
            
    except Exception as e:
        print(f"Error in skin tone detection: {str(e)}")
        return "Medium"  # Default fallback

def get_color_recommendations(skin_tone: str) -> List[str]:
    """
    Get color recommendations for a given skin tone.
    
    Args:
        skin_tone: String representing the skin tone category
        
    Returns:
        List of hex color codes recommended for the skin tone
    """
    if skin_tone in COLOR_RECOMMENDATIONS:
        return COLOR_RECOMMENDATIONS[skin_tone]
    else:
        # Default recommendations if skin tone not recognized
        return COLOR_RECOMMENDATIONS["Medium"]

def adjust_skin_tone(image: np.ndarray, target_tone: str) -> np.ndarray:
    """
    Adjust the skin tone of an image to match a target tone.
    
    Args:
        image: RGB image as numpy array
        target_tone: Target skin tone category
        
    Returns:
        Adjusted RGB image as numpy array
    """
    try:
        # Convert to LAB color space
        lab_image = color.rgb2lab(image)
        
        # Create a skin mask
        l_range = (30, 90)
        a_range = (0, 35)
        b_range = (5, 45)
        
        skin_mask = (
            (lab_image[:,:,0] >= l_range[0]) & (lab_image[:,:,0] <= l_range[1]) &
            (lab_image[:,:,1] >= a_range[0]) & (lab_image[:,:,1] <= a_range[1]) &
            (lab_image[:,:,2] >= b_range[0]) & (lab_image[:,:,2] <= b_range[1])
        )
        
        # Target L values for each skin tone
        target_l_values = {
            "Fair": 78,
            "Light": 72,
            "Medium": 65,
            "Olive": 62,
            "Tan": 58,
            "Deep": 52,
            "Dark": 45
        }
        
        # Target a and b adjustments (subtle changes to maintain realism)
        target_a_adjustments = {
            "Fair": -2,    # Less red
            "Light": -1,   # Slightly less red
            "Medium": 0,   # No change
            "Olive": 1,    # Slightly more green-yellow
            "Tan": 2,      # More yellow-orange
            "Deep": 3,     # More red-orange
            "Dark": 4      # More red
        }
        
        target_b_adjustments = {
            "Fair": -2,    # Less yellow
            "Light": -1,   # Slightly less yellow
            "Medium": 0,   # No change
            "Olive": 2,    # More yellow
            "Tan": 4,      # More yellow-orange
            "Deep": 5,     # More yellow-red
            "Dark": 6      # More yellow-red
        }
        
        # Get current average L value of skin
        current_l = np.mean(lab_image[:,:,0][skin_mask]) if np.sum(skin_mask) > 0 else 65
        
        # Calculate adjustment factor
        target_l = target_l_values.get(target_tone, 65)
        l_adjustment = target_l - current_l
        
        # Get a and b adjustments
        a_adjustment = target_a_adjustments.get(target_tone, 0)
        b_adjustment = target_b_adjustments.get(target_tone, 0)
        
        # Create adjusted image
        adjusted_lab = lab_image.copy()
        
        # Apply adjustments only to skin pixels
        adjusted_lab[:,:,0][skin_mask] = np.clip(adjusted_lab[:,:,0][skin_mask] + l_adjustment, 0, 100)
        adjusted_lab[:,:,1][skin_mask] = np.clip(adjusted_lab[:,:,1][skin_mask] + a_adjustment, -127, 127)
        adjusted_lab[:,:,2][skin_mask] = np.clip(adjusted_lab[:,:,2][skin_mask] + b_adjustment, -127, 127)
        
        # Convert back to RGB
        adjusted_rgb = color.lab2rgb(adjusted_lab)
        
        # Ensure proper range and type
        adjusted_rgb = np.clip(adjusted_rgb * 255, 0, 255).astype(np.uint8)
        
        return adjusted_rgb
        
    except Exception as e:
        print(f"Error adjusting skin tone: {str(e)}")
        return image  # Return original image on error