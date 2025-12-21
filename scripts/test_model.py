"""
Test script for the trained model

Usage:
  python scripts/test_model.py --image path/to/image.jpg
  python scripts/test_model.py --batch path/to/folder/
"""

import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.inference import detect_deepfake, analyze_image_detailed

def test_single_image(image_path):
    """Test on a single image"""
    print("=" * 60)
    print("DEEPFAKE DETECTION - SINGLE IMAGE TEST")
    print("=" * 60)
    print(f"Image: {image_path}")
    print()
    
    result = analyze_image_detailed(image_path)
    
    print("PREDICTION RESULTS:")
    print("-" * 60)
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Probability Real: {result['probability_real']:.2%}")
    print(f"Probability Fake: {result['probability_fake']:.2%}")
    print(f"Threshold: {result['threshold']:.3f}")
    print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
    
    if 'feature_importance' in result:
        print()
        print("FEATURE IMPORTANCE:")
        print("-" * 60)
        for feature_name, importance in result['feature_importance'].items():
            print(f"{feature_name.upper()}: {importance:.2%}")
    
    print("=" * 60)

def test_batch(folder_path):
    """Test on multiple images"""
    folder = Path(folder_path)
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    image_files = [f for f in folder.glob('*') if f.suffix.lower() in image_extensions]
    
    if not image_files:
        print(f"No images found in {folder_path}")
        return
    
    print("=" * 60)
    print("DEEPFAKE DETECTION - BATCH TEST")
    print("=" * 60)
    print(f"Folder: {folder_path}")
    print(f"Found {len(image_files)} images")
    print()
    
    results = []
    for i, image_file in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] Processing {image_file.name}...")
        result = detect_deepfake(str(image_file))
        result['filename'] = image_file.name
        results.append(result)
    
    print()
    print("BATCH RESULTS:")
    print("-" * 60)
    
    fake_count = sum(1 for r in results if r['is_fake'])
    real_count = len(results) - fake_count
    
    print(f"Total Images: {len(results)}")
    print(f"Detected as Real: {real_count}")
    print(f"Detected as Fake: {fake_count}")
    print()
    
    print("DETAILED RESULTS:")
    print("-" * 60)
    for result in results:
        status = "FAKE" if result['is_fake'] else "REAL"
        print(f"{result['filename']:30s} | {status:4s} | Confidence: {result['confidence']:.2%}")
    
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test deepfake detection model')
    parser.add_argument('--image', type=str, help='Path to single image')
    parser.add_argument('--batch', type=str, help='Path to folder of images')
    
    args = parser.parse_args()
    
    if args.image:
        test_single_image(args.image)
    elif args.batch:
        test_batch(args.batch)
    else:
        print("Please provide either --image or --batch argument")
        print()
        print("Examples:")
        print("  python scripts/test_model.py --image path/to/image.jpg")
        print("  python scripts/test_model.py --batch path/to/folder/")
