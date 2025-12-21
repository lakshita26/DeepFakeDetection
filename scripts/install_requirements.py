#!/usr/bin/env python3
"""
Install Python requirements for the deepfake detection model
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required Python packages"""
    
    requirements = [
        'torch>=2.0.0',
        'torchvision>=0.15.0',
        'opencv-python>=4.8.0',
        'numpy>=1.24.0',
        'scikit-learn>=1.3.0',
        'dlib>=19.24.0',
        'Pillow>=10.0.0',
        'joblib>=1.3.0',
        'efficientnet-pytorch>=0.7.1'
    ]
    
    print("Installing Python requirements...")
    
    for requirement in requirements:
        try:
            print(f"Installing {requirement}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', requirement])
            print(f"✓ {requirement} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {requirement}: {e}")
            return False
    
    print("All requirements installed successfully!")
    return True

if __name__ == '__main__':
    success = install_requirements()
    if not success:
        sys.exit(1)
