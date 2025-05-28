# Skin Tone Color Advisor

An interactive web application that analyzes skin tones in uploaded photos and provides personalized color recommendations. The app also allows users to visualize how different skin tones would look with various color palettes.

## Features

- **Image Upload**: Upload photos to analyze skin tone
- **Skin Tone Detection**: Automatically detects the dominant skin tone in the image
- **Color Recommendations**: Provides a palette of colors that complement the detected skin tone
- **Skin Tone Adjustment**: Simulate how different skin tones would look with various color palettes

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py
```

4. Open your browser and navigate to `http://localhost:8000`

## How It Works

1. **Upload a Photo**: The app accepts JPG and PNG images
2. **Skin Tone Analysis**: The app uses color space analysis to detect the dominant skin tone
3. **Color Recommendations**: Based on the detected skin tone, the app suggests complementary colors
4. **Skin Tone Adjustment**: You can adjust the skin tone to see how different colors would look

## Technical Details

- Built with NiceGUI for the user interface
- Uses PIL and scikit-image for image processing
- Implements LAB color space analysis for accurate skin tone detection
- Provides real-time image adjustments and color recommendations

## Requirements

- Python 3.9+
- Dependencies listed in requirements.txt