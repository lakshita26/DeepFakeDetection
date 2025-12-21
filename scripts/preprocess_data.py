import cv2
import numpy as np
from pathlib import Path
import json
from sklearn.model_selection import train_test_split
import albumentations as A
from albumentations.pytorch import ToTensorV2
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import os

class DeepfakeDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None, image_size=224):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
        self.image_size = image_size
        
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        label = self.labels[idx]
        
        # Load image
        image = cv2.imread(str(image_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize
        image = cv2.resize(image, (self.image_size, self.image_size))
        
        # Apply transforms
        if self.transform:
            augmented = self.transform(image=image)
            image = augmented['image']
        
        return image, torch.tensor(label, dtype=torch.float32)

class DataPreprocessor:
    def __init__(self, data_dir="./datasets", image_size=224):
        self.data_dir = Path(data_dir)
        self.image_size = image_size
        
    def create_train_val_split(self, test_size=0.2, random_state=42):
        """Create train/validation split from datasets"""
        print("Creating train/validation split...")
        
        # Collect all image paths and labels
        image_paths = []
        labels = []
        
        # FFHQ images (real)
        ffhq_dir = self.data_dir / "ffhq" / "images"
        if ffhq_dir.exists():
            for img_path in ffhq_dir.glob("*.jpg"):
                image_paths.append(img_path)
                labels.append(1)  # Real = 1
                
        # FaceForensics real images
        ff_real_dir = self.data_dir / "faceforensics" / "real"
        if ff_real_dir.exists():
            for img_path in ff_real_dir.glob("*.jpg"):
                image_paths.append(img_path)
                labels.append(1)  # Real = 1
                
        # FaceForensics fake images
        ff_fake_dir = self.data_dir / "faceforensics" / "fake"
        if ff_fake_dir.exists():
            for img_path in ff_fake_dir.glob("*.jpg"):
                image_paths.append(img_path)
                labels.append(0)  # Fake = 0
        
        print(f"Total images: {len(image_paths)}")
        print(f"Real images: {sum(labels)}")
        print(f"Fake images: {len(labels) - sum(labels)}")
        
        # Split data
        train_paths, val_paths, train_labels, val_labels = train_test_split(
            image_paths, labels, test_size=test_size, random_state=random_state, stratify=labels
        )
        
        return train_paths, val_paths, train_labels, val_labels
    
    def get_transforms(self):
        """Get data augmentation transforms"""
        train_transform = A.Compose([
            A.HorizontalFlip(p=0.5),
            A.RandomBrightnessContrast(p=0.3),
            A.HueSaturationValue(p=0.3),
            A.GaussNoise(p=0.2),
            A.MotionBlur(p=0.2),
            A.MedianBlur(blur_limit=3, p=0.1),
            A.Blur(blur_limit=3, p=0.1),
            A.CLAHE(p=0.2),
            A.RandomGamma(p=0.2),
            A.ImageCompression(quality_lower=60, quality_upper=100, p=0.5),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
        
        val_transform = A.Compose([
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
        
        return train_transform, val_transform
    
    def create_dataloaders(self, batch_size=32, num_workers=4):
        """Create PyTorch DataLoaders"""
        train_paths, val_paths, train_labels, val_labels = self.create_train_val_split()
        train_transform, val_transform = self.get_transforms()
        
        # Create datasets
        train_dataset = DeepfakeDataset(
            train_paths, train_labels, train_transform, self.image_size
        )
        val_dataset = DeepfakeDataset(
            val_paths, val_labels, val_transform, self.image_size
        )
        
        # Create dataloaders
        train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True, 
            num_workers=num_workers, pin_memory=True
        )
        val_loader = DataLoader(
            val_dataset, batch_size=batch_size, shuffle=False,
            num_workers=num_workers, pin_memory=True
        )
        
        return train_loader, val_loader
    
    def analyze_dataset_statistics(self):
        """Analyze dataset statistics"""
        train_paths, val_paths, train_labels, val_labels = self.create_train_val_split()
        
        stats = {
            "total_images": len(train_paths) + len(val_paths),
            "train_images": len(train_paths),
            "val_images": len(val_paths),
            "train_real": sum(train_labels),
            "train_fake": len(train_labels) - sum(train_labels),
            "val_real": sum(val_labels),
            "val_fake": len(val_labels) - sum(val_labels)
        }
        
        print("Dataset Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        return stats

if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    preprocessor.analyze_dataset_statistics()
    
    # Create sample dataloaders
    train_loader, val_loader = preprocessor.create_dataloaders(batch_size=16)
    print(f"Train batches: {len(train_loader)}")
    print(f"Val batches: {len(val_loader)}")
    
    # Test loading a batch
    for batch_idx, (images, labels) in enumerate(train_loader):
        print(f"Batch {batch_idx}: Images shape: {images.shape}, Labels shape: {labels.shape}")
        break
