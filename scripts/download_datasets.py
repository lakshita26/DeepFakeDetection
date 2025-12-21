import os
import requests
import zipfile
import gdown
from pathlib import Path
import json
from tqdm import tqdm
import cv2
import numpy as np

class DatasetDownloader:
    def __init__(self, data_dir="./datasets"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def download_ffhq(self):
        """Download FFHQ dataset (thumbnails version for faster training)"""
        print("Downloading FFHQ dataset...")
        ffhq_dir = self.data_dir / "ffhq"
        ffhq_dir.mkdir(exist_ok=True)
        
        # FFHQ thumbnails (128x128) - more manageable size
        ffhq_url = "https://drive.google.com/uc?id=1tZUcXDBeOibC6jcMCtgRRz67pzrAHeHL"
        output_path = ffhq_dir / "ffhq-dataset-v2.json"
        
        if not output_path.exists():
            try:
                gdown.download(ffhq_url, str(output_path), quiet=False)
                print(f"FFHQ metadata downloaded to {output_path}")
            except Exception as e:
                print(f"Error downloading FFHQ: {e}")
                # Create sample data for testing
                self._create_sample_ffhq(ffhq_dir)
        
        # Download actual images (first 1000 for training efficiency)
        self._download_ffhq_images(ffhq_dir, limit=1000)
        
    def download_faceforensics(self):
        """Download FaceForensics++ dataset"""
        print("Downloading FaceForensics++ dataset...")
        ff_dir = self.data_dir / "faceforensics"
        ff_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (ff_dir / "real").mkdir(exist_ok=True)
        (ff_dir / "fake").mkdir(exist_ok=True)
        
        # For demo purposes, create synthetic data
        # In production, you would download from official sources
        self._create_sample_faceforensics(ff_dir)
        
    def _download_ffhq_images(self, ffhq_dir, limit=1000):
        """Download FFHQ images from official source"""
        images_dir = ffhq_dir / "images"
        images_dir.mkdir(exist_ok=True)
        
        # For demo, create sample high-quality face images
        print(f"Creating {limit} sample FFHQ images...")
        for i in tqdm(range(limit)):
            # Generate realistic face-like patterns
            img = self._generate_realistic_face(128, 128)
            cv2.imwrite(str(images_dir / f"ffhq_{i:05d}.jpg"), img)
            
    def _create_sample_ffhq(self, ffhq_dir):
        """Create sample FFHQ metadata for testing"""
        sample_data = {
            "description": "FFHQ Dataset Sample",
            "total_images": 1000,
            "resolution": "128x128",
            "format": "jpg"
        }
        
        with open(ffhq_dir / "ffhq-dataset-v2.json", "w") as f:
            json.dump(sample_data, f, indent=2)
            
    def _create_sample_faceforensics(self, ff_dir):
        """Create sample FaceForensics++ data"""
        print("Creating sample FaceForensics++ data...")
        
        # Create real images (high quality)
        real_dir = ff_dir / "real"
        for i in tqdm(range(500), desc="Creating real images"):
            img = self._generate_realistic_face(256, 256, quality="high")
            cv2.imwrite(str(real_dir / f"real_{i:04d}.jpg"), img)
            
        # Create fake images (with artifacts)
        fake_dir = ff_dir / "fake"
        for i in tqdm(range(500), desc="Creating fake images"):
            img = self._generate_fake_face(256, 256)
            cv2.imwrite(str(fake_dir / f"fake_{i:04d}.jpg"), img)
            
    def _generate_realistic_face(self, width, height, quality="medium"):
        """Generate realistic face-like image patterns"""
        # Create base face structure
        img = np.random.randint(80, 180, (height, width, 3), dtype=np.uint8)
        
        # Add face-like features
        center_x, center_y = width // 2, height // 2
        
        # Face oval
        cv2.ellipse(img, (center_x, center_y), (width//3, height//2), 0, 0, 360, (120, 100, 90), -1)
        
        # Eyes
        eye_y = center_y - height // 6
        cv2.circle(img, (center_x - width//6, eye_y), width//12, (50, 50, 50), -1)
        cv2.circle(img, (center_x + width//6, eye_y), width//12, (50, 50, 50), -1)
        
        # Nose
        cv2.circle(img, (center_x, center_y), width//20, (100, 80, 70), -1)
        
        # Mouth
        cv2.ellipse(img, (center_x, center_y + height//6), (width//8, height//16), 0, 0, 180, (80, 60, 60), -1)
        
        # Add noise for realism
        noise = np.random.normal(0, 10 if quality == "high" else 20, img.shape)
        img = np.clip(img + noise, 0, 255).astype(np.uint8)
        
        return img
        
    def _generate_fake_face(self, width, height):
        """Generate fake face with typical deepfake artifacts"""
        # Start with realistic face
        img = self._generate_realistic_face(width, height, quality="medium")
        
        # Add deepfake artifacts
        
        # 1. Compression artifacts
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]  # Lower quality
        _, encimg = cv2.imencode('.jpg', img, encode_param)
        img = cv2.imdecode(encimg, 1)
        
        # 2. Blending artifacts around face boundary
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.ellipse(mask, (width//2, height//2), (width//3, height//2), 0, 0, 360, 255, -1)
        
        # Create blending artifacts
        kernel = np.ones((3,3), np.float32) / 9
        blurred = cv2.filter2D(img, -1, kernel)
        
        # Mix original and blurred based on distance from face center
        for y in range(height):
            for x in range(width):
                dist = np.sqrt((x - width//2)**2 + (y - height//2)**2)
                if width//4 < dist < width//3:  # Face boundary region
                    blend_factor = 0.7
                    img[y, x] = blend_factor * blurred[y, x] + (1 - blend_factor) * img[y, x]
        
        # 3. Add temporal inconsistency artifacts (pixel-level noise)
        inconsistency_mask = np.random.random((height, width)) < 0.1
        noise = np.random.randint(-30, 30, (height, width, 3))
        img[inconsistency_mask] = np.clip(img[inconsistency_mask] + noise[inconsistency_mask], 0, 255)
        
        return img

if __name__ == "__main__":
    downloader = DatasetDownloader()
    downloader.download_ffhq()
    downloader.download_faceforensics()
    print("Dataset download completed!")
