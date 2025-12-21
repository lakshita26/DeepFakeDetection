import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import json
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

from model import HybridFusionModel, ModelTrainer
from features import FeatureExtractor

class DeepfakeDataset(Dataset):
    def __init__(self, processed_csv_path, feature_extractor):
        self.df = pd.read_csv(processed_csv_path)
        self.feature_extractor = feature_extractor
        
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        
        # Load preprocessed images
        normalized_image = np.load(row['norm_path'])
        gray_image = np.load(row['gray_path'])
        
        # Extract features
        features = self.feature_extractor.extract_all_features(normalized_image, gray_image)
        
        return {
            'lbph': torch.FloatTensor(features['lbph']),
            'fisherface': torch.FloatTensor(features['fisherface']),
            'efficientnet': torch.FloatTensor(features['efficientnet']),
            'label': torch.LongTensor([row['label']])[0]
        }

def prepare_feature_extractors():
    """Prepare and fit feature extractors"""
    print("Preparing feature extractors...")
    
    feature_extractor = FeatureExtractor()
    
    # Load training data to fit classical extractors
    train_df = pd.read_csv("data/processed/train/processed_data.csv")
    
    # Load grayscale images for fitting Fisherface
    print("Loading training images for Fisherface fitting...")
    gray_images = []
    labels = []
    
    for idx, row in tqdm(train_df.iterrows(), total=len(train_df)):
        gray_image = np.load(row['gray_path'])
        gray_images.append(gray_image)
        labels.append(row['label'])
        
        # Limit for memory efficiency
        if len(gray_images) >= 5000:
            break
    
    gray_images = np.array(gray_images)
    labels = np.array(labels)
    
    # Fit classical extractors
    feature_extractor.fit_classical_extractors(gray_images, labels)
    
    # Save fitted extractors
    feature_extractor.save_extractors("models/extractors")
    
    return feature_extractor

def create_data_loaders(feature_extractor, batch_size=32):
    """Create data loaders"""
    print("Creating data loaders...")
    
    # Create datasets
    train_dataset = DeepfakeDataset("data/processed/train/processed_data.csv", feature_extractor)
    val_dataset = DeepfakeDataset("data/processed/val/processed_data.csv", feature_extractor)
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True, 
        num_workers=4,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=batch_size, 
        shuffle=False, 
        num_workers=4,
        pin_memory=True
    )
    
    return train_loader, val_loader

def plot_training_history(train_losses, val_losses, train_accs, val_accs):
    """Plot training history"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Loss plot
    ax1.plot(train_losses, label='Train Loss', color='blue')
    ax1.plot(val_losses, label='Val Loss', color='red')
    ax1.set_title('Training and Validation Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True)
    
    # Accuracy plot
    ax2.plot(train_accs, label='Train Accuracy', color='blue')
    ax2.plot(val_accs, label='Val Accuracy', color='red')
    ax2.set_title('Training and Validation Accuracy')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy (%)')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('training_history.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main training function"""
    print("Starting deepfake detection training...")
    
    # Load configuration
    with open("config.json", 'r') as f:
        config = json.load(f)
    
    # Create models directory
    Path("models").mkdir(exist_ok=True)
    
    # Prepare feature extractors
    feature_extractor = prepare_feature_extractors()
    
    # Create data loaders
    train_loader, val_loader = create_data_loaders(
        feature_extractor, 
        batch_size=config['data']['batch_size']
    )
    
    print(f"Training samples: {len(train_loader.dataset)}")
    print(f"Validation samples: {len(val_loader.dataset)}")
    
    # Create model
    model = HybridFusionModel()
    trainer = ModelTrainer(model)
    
    print(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")
    print(f"Training on device: {trainer.device}")
    
    # Training loop
    train_losses = []
    val_losses = []
    train_accs = []
    val_accs = []
    
    best_val_acc = 0
    epochs = config['training']['epochs']
    
    for epoch in range(epochs):
        print(f"\nEpoch {epoch+1}/{epochs}")
        print("-" * 50)
        
        # Train
        train_loss, train_acc = trainer.train_epoch(train_loader)
        
        # Validate
        val_loss, val_acc = trainer.validate(val_loader)
        
        # Update scheduler
        if trainer.scheduler:
            trainer.scheduler.step()
        
        # Record metrics
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)
        
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': trainer.optimizer.state_dict(),
                'val_acc': val_acc,
                'val_loss': val_loss,
                'config': config
            }, 'models/best_model.pth')
            print(f"New best model saved! Val Acc: {val_acc:.2f}%")
        
        # Early stopping
        if trainer.should_stop_early(val_loss):
            print(f"Early stopping triggered after {epoch+1} epochs")
            break
    
    # Plot training history
    plot_training_history(train_losses, val_losses, train_accs, val_accs)
    
    # Save final model
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': trainer.optimizer.state_dict(),
        'train_losses': train_losses,
        'val_losses': val_losses,
        'train_accs': train_accs,
        'val_accs': val_accs,
        'config': config
    }, 'models/final_model.pth')
    
    print(f"\nTraining completed!")
    print(f"Best validation accuracy: {best_val_acc:.2f}%")
    print("Models saved in 'models/' directory")

if __name__ == "__main__":
    main()
