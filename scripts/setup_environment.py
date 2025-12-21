import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "data/processed",
        "data/processed/train",
        "data/processed/val", 
        "data/processed/test",
        "models",
        "models/extractors",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def setup_kaggle():
    """Setup Kaggle API"""
    print("\nSetting up Kaggle API...")
    print("Please ensure you have:")
    print("1. Created a Kaggle account")
    print("2. Downloaded your kaggle.json API key")
    print("3. Placed it in ~/.kaggle/kaggle.json (Linux/Mac) or C:\\Users\\<username>\\.kaggle\\kaggle.json (Windows)")
    print("4. Set permissions: chmod 600 ~/.kaggle/kaggle.json")
    
    try:
        import kaggle
        print("Kaggle API is properly configured!")
        return True
    except Exception as e:
        print(f"Kaggle API setup issue: {e}")
        return False

def main():
    """Main setup function"""
    print("Setting up Deepfake Detection Environment...")
    print("=" * 50)
    
    # Create directories
    print("\n1. Creating directories...")
    create_directories()
    
    # Install requirements
    print("\n2. Installing requirements...")
    if not install_requirements():
        print("Failed to install requirements. Please install manually.")
        return
    
    # Setup Kaggle
    print("\n3. Checking Kaggle setup...")
    setup_kaggle()
    
    # Download face predictor
    print("\n4. Downloading face landmark predictor...")
    try:
        from scripts.download_predictor import download_dlib_predictor
        download_dlib_predictor()
    except Exception as e:
        print(f"Error downloading predictor: {e}")
    
    print("\n" + "=" * 50)
    print("Setup completed!")
    print("\nNext steps:")
    print("1. Run 'python prepare_data.py' to download and prepare datasets")
    print("2. Run 'python preprocess.py' to preprocess images")
    print("3. Run 'python train.py' to train the model")
    print("4. Run 'python eval.py' to evaluate the model")
    print("5. Run 'python serve.py' to start the API server")

if __name__ == "__main__":
    main()
