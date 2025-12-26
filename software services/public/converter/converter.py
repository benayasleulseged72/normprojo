"""
BLSC Image Converter - Python Version
=====================================
Convert images between formats: PNG, JPG, BMP, ICO, WEBP, GIF

Requirements:
    pip install Pillow

Usage:
    python converter.py input.png output.jpg
    python converter.py input.jpg output.ico
    python converter.py input.bmp output.png

Author: BLSC - Benayas Leulseged Software Company
Date: December 2024
"""

import sys
import os
from PIL import Image

# Supported formats
SUPPORTED_FORMATS = {
    'png': 'PNG',
    'jpg': 'JPEG',
    'jpeg': 'JPEG',
    'bmp': 'BMP',
    'ico': 'ICO',
    'webp': 'WEBP',
    'gif': 'GIF',
    'tiff': 'TIFF',
    'tif': 'TIFF'
}

def convert_image(input_path, output_path, quality=95):
    """
    Convert an image from one format to another.
    
    Args:
        input_path: Path to input image
        output_path: Path for output image (format determined by extension)
        quality: Quality for lossy formats (1-100)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Open the image
        img = Image.open(input_path)
        
        # Get output format from extension
        output_ext = os.path.splitext(output_path)[1].lower().replace('.', '')
        
        if output_ext not in SUPPORTED_FORMATS:
            print(f"Error: Unsupported output format '{output_ext}'")
            print(f"Supported formats: {', '.join(SUPPORTED_FORMATS.keys())}")
            return False
        
        output_format = SUPPORTED_FORMATS[output_ext]
        
        # Handle special cases
        if output_format == 'JPEG':
            # JPEG doesn't support transparency, convert to RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
        
        elif output_format == 'ICO':
            # ICO needs specific sizes
            sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
            # Resize to fit in 256x256 while maintaining aspect ratio
            img.thumbnail((256, 256), Image.Resampling.LANCZOS)
            img.save(output_path, format='ICO', sizes=[(img.width, img.height)])
            print(f"✅ Converted: {input_path} → {output_path}")
            print(f"   Size: {img.width}x{img.height}")
            return True
        
        elif output_format == 'PNG':
            # Ensure RGBA for PNG
            if img.mode not in ('RGBA', 'RGB', 'L', 'LA'):
                img = img.convert('RGBA')
        
        elif output_format == 'BMP':
            # BMP needs RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
        
        # Save the image
        save_kwargs = {}
        if output_format in ('JPEG', 'WEBP'):
            save_kwargs['quality'] = quality
        if output_format == 'PNG':
            save_kwargs['optimize'] = True
        
        img.save(output_path, format=output_format, **save_kwargs)
        
        # Get file sizes
        input_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)
        
        print(f"✅ Converted: {input_path} → {output_path}")
        print(f"   Original: {format_size(input_size)}")
        print(f"   Converted: {format_size(output_size)}")
        print(f"   Dimensions: {img.width}x{img.height}")
        
        return True
        
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def format_size(bytes):
    """Format file size in human readable format"""
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.1f} KB"
    else:
        return f"{bytes / (1024 * 1024):.1f} MB"

def batch_convert(input_folder, output_folder, output_format):
    """
    Convert all images in a folder to a specific format.
    
    Args:
        input_folder: Folder containing images
        output_folder: Folder for converted images
        output_format: Target format (png, jpg, etc.)
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    converted = 0
    failed = 0
    
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        
        # Skip non-files
        if not os.path.isfile(input_path):
            continue
        
        # Check if it's an image
        ext = os.path.splitext(filename)[1].lower().replace('.', '')
        if ext not in SUPPORTED_FORMATS:
            continue
        
        # Create output path
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_folder, f"{base_name}.{output_format}")
        
        if convert_image(input_path, output_path):
            converted += 1
        else:
            failed += 1
    
    print(f"\n📊 Batch conversion complete!")
    print(f"   Converted: {converted}")
    print(f"   Failed: {failed}")

def interactive_mode():
    """Run converter in interactive mode"""
    print("\n" + "="*50)
    print("  BLSC Image Converter - Interactive Mode")
    print("="*50)
    print("\nSupported formats:", ", ".join(SUPPORTED_FORMATS.keys()))
    
    while True:
        print("\n" + "-"*40)
        input_path = input("Enter input image path (or 'quit' to exit): ").strip()
        
        if input_path.lower() in ('quit', 'exit', 'q'):
            print("Goodbye! 👋")
            break
        
        if not os.path.exists(input_path):
            print("❌ File not found!")
            continue
        
        print("\nAvailable output formats:")
        for i, fmt in enumerate(SUPPORTED_FORMATS.keys(), 1):
            print(f"  {i}. {fmt.upper()}")
        
        format_choice = input("Enter output format (e.g., png, jpg): ").strip().lower()
        
        if format_choice not in SUPPORTED_FORMATS:
            print("❌ Invalid format!")
            continue
        
        # Generate output path
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_converted.{format_choice}"
        
        custom_path = input(f"Output path [{output_path}]: ").strip()
        if custom_path:
            output_path = custom_path
        
        convert_image(input_path, output_path)

def main():
    """Main entry point"""
    if len(sys.argv) == 1:
        # No arguments - run interactive mode
        interactive_mode()
    
    elif len(sys.argv) == 3:
        # Two arguments - convert single file
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        success = convert_image(input_path, output_path)
        sys.exit(0 if success else 1)
    
    elif len(sys.argv) == 4 and sys.argv[1] == '--batch':
        # Batch mode
        input_folder = sys.argv[2]
        output_format = sys.argv[3]
        output_folder = input_folder + '_converted'
        batch_convert(input_folder, output_folder, output_format)
    
    else:
        print("BLSC Image Converter")
        print("="*40)
        print("\nUsage:")
        print("  python converter.py                     # Interactive mode")
        print("  python converter.py input.png output.jpg  # Convert single file")
        print("  python converter.py --batch folder png    # Batch convert folder")
        print("\nSupported formats:", ", ".join(SUPPORTED_FORMATS.keys()))

if __name__ == '__main__':
    main()
