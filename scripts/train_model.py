"""
Training script for deepfake detection model

Usage:
  python scripts/train_model.py

This will:
1. Generate sample training data (or use your own data)
2. Train the hybrid fusion model
3. Save the best model and feature extractors
4. Generate training history plots
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.train import train_model

if __name__ == "__main__":
    print("Starting deepfake detection model training...")
    print("This may take several minutes depending on your hardware.")
    print()
    
    try:
        train_model()
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
    except Exception as e:
        print(f"\n\nError during training: {e}")
        import traceback
        traceback.print_exc()
