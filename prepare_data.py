import os
import json
import requests
import zipfile
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import kaggle

class DatasetPreparer:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
    def download_ffhq(self):
        """Download FFHQ dataset"""
        print("Downloading FFHQ dataset...")
        ffhq_dir = self.data_dir / "ffhq"
        ffhq_dir.mkdir(exist_ok=True)
        
        # Download FFHQ thumbnails (real faces)
        url = "https://drive.google.com/uc?id=1tZUcXDBeOibC6jcMCtgRRz67pzrAHeHL"
        output_path = ffhq_dir / "ffhq-dataset-v2.json"
        
        if not output_path.exists():
            print("Please manually download FFHQ from https://github.com/NVlabs/ffhq-dataset")
            print("Place the images in data/ffhq/images/")
        
        return ffhq_dir
    
    def download_faceforensics(self):
        """Download FaceForensics++ dataset"""
        print("Downloading FaceForensics++ dataset...")
        ff_dir = self.data_dir / "faceforensics"
        ff_dir.mkdir(exist_ok=True)
        
        # Note: FaceForensics++ requires registration
        print("Please register and download FaceForensics++ from:")
        print("https://github.com/ondyari/FaceForensics")
        print("Place the dataset in data/faceforensics/")
        
        return ff_dir
    
    def download_dfdc(self):
        """Download DFDC dataset via Kaggle"""
        print("Downloading DFDC dataset...")
        dfdc_dir = self.data_dir / "dfdc"
        dfdc_dir.mkdir(exist_ok=True)
        
        try:
            # Download DFDC preview dataset
            kaggle.api.competition_download_files(
                'deepfake-detection-challenge',
                path=str(dfdc_dir),
                unzip=True
            )
        except Exception as e:
            print(f"Error downloading DFDC: {e}")
            print("Please manually download from Kaggle DFDC competition")
        
        return dfdc_dir
    
    def create_dataset_splits(self):
        """Create train/val/test splits"""
        print("Creating dataset splits...")
        
        # Collect all image paths and labels
        all_data = []
        
        # FFHQ (real images)
        ffhq_dir = self.data_dir / "ffhq" / "images"
        if ffhq_dir.exists():
            for img_path in ffhq_dir.glob("*.png"):
                all_data.append({
                    'path': str(img_path),
                    'label': 0,  # real
                    'dataset': 'ffhq'
                })
        
        # FaceForensics++ (fake images)
        ff_dir = self.data_dir / "faceforensics"
        if ff_dir.exists():
            for method_dir in ff_dir.glob("*/"):
                if method_dir.name in ['Deepfakes', 'Face2Face', 'FaceSwapper', 'NeuralTextures']:
                    for img_path in method_dir.glob("**/*.png"):
                        all_data.append({
                            'path': str(img_path),
                            'label': 1,  # fake
                            'dataset': 'faceforensics',
                            'method': method_dir.name
                        })
        
        # DFDC
        dfdc_dir = self.data_dir / "dfdc"
        if dfdc_dir.exists():
            # Load DFDC metadata
            metadata_path = dfdc_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                for filename, info in metadata.items():
                    img_path = dfdc_dir / filename
                    if img_path.exists():
                        all_data.append({
                            'path': str(img_path),
                            'label': 1 if info['label'] == 'FAKE' else 0,
                            'dataset': 'dfdc'
                        })
        
        # Create DataFrame and split
        df = pd.DataFrame(all_data)
        
        # Stratified split
        from sklearn.model_selection import train_test_split
        
        train_df, temp_df = train_test_split(
            df, 
            test_size=1-self.config['data']['train_split'],
            stratify=df['label'],
            random_state=42
        )
        
        val_size = self.config['data']['val_split'] / (1 - self.config['data']['train_split'])
        val_df, test_df = train_test_split(
            temp_df,
            test_size=1-val_size,
            stratify=temp_df['label'],
            random_state=42
        )
        
        # Save splits
        train_df.to_csv(self.data_dir / "train.csv", index=False)
        val_df.to_csv(self.data_dir / "val.csv", index=False)
        test_df.to_csv(self.data_dir / "test.csv", index=False)
        
        print(f"Dataset splits created:")
        print(f"Train: {len(train_df)} samples")
        print(f"Val: {len(val_df)} samples")
        print(f"Test: {len(test_df)} samples")
        
        return train_df, val_df, test_df

if __name__ == "__main__":
    preparer = DatasetPreparer()
    
    # Download datasets
    preparer.download_ffhq()
    preparer.download_faceforensics()
    preparer.download_dfdc()
    
    # Create splits
    preparer.create_dataset_splits()
