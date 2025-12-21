#!/usr/bin/env python3
"""
Complete system setup script
Downloads datasets, prepares data, and trains models
"""

import subprocess
import sys
from pathlib import Path
import argparse

def run_command(cmd, description):
    """Run command with description"""
    print("\n" + "="*60)
    print(f"STEP: {description}")
    print("="*60)
    print(f"Command: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"\n❌ Error in: {description}")
        print("You may need to manually complete this step")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print(f"\n✅ Completed: {description}")

def main():
    parser = argparse.ArgumentParser(description="Setup complete deepfake detection system")
    parser.add_argument('--skip-download', action='store_true', 
                       help='Skip dataset download (if already downloaded)')
    parser.add_argument('--skip-prepare', action='store_true',
                       help='Skip dataset preparation (if already prepared)')
    parser.add_argument('--skip-train', action='store_true',
                       help='Skip model training (if already trained)')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs')
    parser.add_argument('--dataset', type=str, default='all',
                       choices=['all', 'ffhq', 'faceforensics', 'dfdc'],
                       help='Which dataset to download')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("DEEPFAKE DETECTION SYSTEM SETUP")
    print("="*60)
    print("\nThis will:")
    print("1. Download datasets (FFHQ, FaceForensics++, DFDC)")
    print("2. Prepare and preprocess data")
    print("3. Train all models")
    print("4. Set up inference server")
    print("\n⚠️  This process will take several hours and requires:")
    print("   - 100+ GB disk space")
    print("   - Good internet connection")
    print("   - GPU recommended for training")
    
    response = input("\nContinue? (y/n): ")
    if response.lower() != 'y':
        print("Setup cancelled")
        sys.exit(0)
    
    # Step 1: Download datasets
    if not args.skip_download:
        if args.dataset == 'all':
            run_command(
                "python ml/datasets/download_datasets.py --all",
                "Downloading all datasets"
            )
        else:
            run_command(
                f"python ml/datasets/download_datasets.py --dataset {args.dataset}",
                f"Downloading {args.dataset} dataset"
            )
    else:
        print("\n⏭️  Skipping dataset download")
    
    # Step 2: Prepare datasets
    if not args.skip_prepare:
        run_command(
            "python ml/datasets/prepare_datasets.py",
            "Preparing datasets (face detection, cropping, splitting)"
        )
    else:
        print("\n⏭️  Skipping dataset preparation")
    
    # Step 3: Train models
    if not args.skip_train:
        run_command(
            f"python ml/train.py --data-dir ml/data/processed --epochs {args.epochs}",
            f"Training models ({args.epochs} epochs)"
        )
    else:
        print("\n⏭️  Skipping model training")
    
    # Step 4: Test inference
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("\n1. Start the inference server:")
    print("   python ml/serve.py --port 8000")
    print("\n2. In another terminal, start Next.js:")
    print("   npm run dev")
    print("\n3. Open http://localhost:3000 and upload an image")
    print("\n4. The system will now use real ML models for detection!")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
