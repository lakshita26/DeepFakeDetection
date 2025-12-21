import requests
import os
from pathlib import Path
import zipfile

def download_dlib_predictor():
    """Download dlib's 68-point face landmark predictor"""
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    predictor_path = models_dir / "shape_predictor_68_face_landmarks.dat"
    
    # Check if already exists
    if predictor_path.exists():
        print("Face landmark predictor already exists!")
        return
    
    print("Downloading dlib face landmark predictor...")
    
    # Download URL
    url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
    
    try:
        # Download file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Save compressed file
        compressed_path = models_dir / "shape_predictor_68_face_landmarks.dat.bz2"
        
        with open(compressed_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("Download completed!")
        
        # Decompress
        print("Decompressing...")
        import bz2
        
        with bz2.BZ2File(compressed_path, 'rb') as f_in:
            with open(predictor_path, 'wb') as f_out:
                f_out.write(f_in.read())
        
        # Remove compressed file
        compressed_path.unlink()
        
        print(f"Face landmark predictor saved to: {predictor_path}")
        
    except Exception as e:
        print(f"Error downloading predictor: {e}")
        print("Please manually download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")

if __name__ == "__main__":
    download_dlib_predictor()
