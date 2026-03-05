#!/usr/bin/env python3
"""
Wave Filter for Images

Applies a sinusoidal wave distortion effect to JPG images.

Usage:
    python wave_filter.py input.jpg output.jpg --wavelength 30 --amplitude 20
    python wave_filter.py input.jpg output.jpg -w 50 -a 15 --direction horizontal
"""

import argparse
import numpy as np
from PIL import Image
import sys

# globals

PHS = 0

# functions

def apply_wave_filter(image, wavelength, amplitude, direction='horizontal', phase = PHS):
    """
    Apply a wave distortion filter to an image.
    
    Parameters:
    -----------
    image : PIL.Image
        Input image
    wavelength : float
        The wavelength of the sine wave in pixels
    amplitude : float
        The amplitude of the wave distortion in pixels
    direction : str
        Direction of the wave: 'horizontal', 'vertical', or 'both'
    
    Returns:
    --------
    PIL.Image
        Wave-filtered image
    """
    img_array = np.array(image)
    height, width = img_array.shape[:2]
    
    # Create output array
    output = np.zeros_like(img_array)
    
    # Create coordinate grids
    y_coords, x_coords = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    
    if direction == 'horizontal':
        # Horizontal wave: displace pixels horizontally based on y-coordinate
        displacement = amplitude * np.sin(2 * np.pi * y_coords / wavelength + phase)
        source_x = x_coords - displacement
        source_y = y_coords
        
    elif direction == 'vertical':
        # Vertical wave: displace pixels vertically based on x-coordinate
        displacement = amplitude * np.sin(2 * np.pi * x_coords / wavelength + phase)
        source_x = x_coords
        source_y = y_coords - displacement
        
    elif direction == 'both':
        # Apply wave in both directions
        displacement_x = amplitude * np.sin(2 * np.pi * y_coords / wavelength + phase)
        displacement_y = amplitude * np.sin(2 * np.pi * x_coords / wavelength + phase)
        source_x = x_coords - displacement_x
        source_y = y_coords - displacement_y
        
    else:
        raise ValueError("Direction must be 'horizontal', 'vertical', or 'both'")
    
    # Clip coordinates to valid range
    source_x = np.clip(source_x, 0, width - 1).astype(int)
    source_y = np.clip(source_y, 0, height - 1).astype(int)
    
    # Apply the mapping
    output = img_array[source_y, source_x]
    
    return Image.fromarray(output)


def main():
    parser = argparse.ArgumentParser(
        description='Apply a wave distortion filter to a JPG image.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python wave_filter.py input.jpg output.jpg --wavelength 50 --amplitude 20
  python wave_filter.py input.jpg output.jpg -w 50 -a 15 --direction vertical
  python wave_filter.py photo.jpg wavy_photo.jpg -w 40 -a 25 --direction both
        """
    )
    
    parser.add_argument('input', help='Input JPG image file')
    parser.add_argument('output', help='Output JPG image file')
    parser.add_argument('-w', '--wavelength', type=float, default=100.0,
                        help='Wavelength of the wave in pixels (default: 100)')
    parser.add_argument('-a', '--amplitude', type=float, default=20.0,
                        help='Amplitude of the wave distortion in pixels (default: 20)')
    parser.add_argument('-d', '--direction', choices=['horizontal', 'vertical', 'both'],
                        default='horizontal',
                        help='Direction of the wave effect (default: horizontal)')
    parser.add_argument('-q', '--quality', type=int, default=95,
                        help='JPG output quality (1-100, default: 95)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if args.wavelength <= 0:
        print("Error: Wavelength must be positive", file=sys.stderr)
        sys.exit(1)
    
    if args.amplitude < 0:
        print("Error: Amplitude must be non-negative", file=sys.stderr)
        sys.exit(1)
    
    if not (1 <= args.quality <= 100):
        print("Error: Quality must be between 1 and 100", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Load the image
        print(f"Loading image: {args.input}")
        image = Image.open(args.input)
        
        # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        print(f"Applying wave filter (wavelength={args.wavelength}, amplitude={args.amplitude}, direction={args.direction})")
        
        # Apply the wave filter
        filtered_image = apply_wave_filter(image, args.wavelength, args.amplitude, args.direction)
        nxtfiltered_image = apply_wave_filter(filtered_image, args.wavelength/2, args.amplitude, args.direction)
        
        # Save the output
        print(f"Saving output: {args.output}")
        #filtered_image.save(args.output, 'JPEG', quality=args.quality)
        nxtfiltered_image.save(args.output, 'JPEG', quality=args.quality)
        
        print("Done!")
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
