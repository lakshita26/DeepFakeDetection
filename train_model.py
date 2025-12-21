import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import numpy as np
import json
import os
from pathlib import Path
import argparse
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

from scripts.preprocess_data import DataPreprocessor
from models.hybrid_model import HybridDeepfakeDetector, create_hybrid_model, create_ensemble_model
from utils.metrics import DeepfakeMetrics
from utils.losses import HybridLoss
from utils.scheduler import get_scheduler

class DeepfakeTrainer:
    def __init__(self, config_path: str):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Setup device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Create directories
        self.setup_directories()
        
        # Initialize components
        self.setup_data()
        self.setup_model()
        self.setup_training()
        self.setup_logging()
        
    def setup_directories(self):
        """Create necessary directories"""
        self.model_dir = Path(self.config['paths']['model_dir'])
        self.logs_dir = Path(self.config['paths']['logs_dir'])
        self.checkpoints_dir = Path(self.config['paths']['checkpoints_dir'])
        
        for dir_path in [self.model_dir, self.logs_dir, self.checkpoints_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def setup_data(self):
        """Setup data loaders"""
        print("Setting up data loaders...")
        
        preprocessor = DataPreprocessor(
            data_dir=self.config['paths']['data_dir'],
            image_size=self.config['model']['image_size']
        )
        
        self.train_loader, self.val_loader = preprocessor.create_dataloaders(
            batch_size=self.config['training']['batch_size'],
            num_workers=self.config['data']['num_workers']
        )
        
        print(f"Train batches: {len(self.train_loader)}")
        print(f"Validation batches: {len(self.val_loader)}")
    
    def setup_model(self):
        """Setup model"""
        print("Setting up model...")
        
        self.model = create_hybrid_model(self.config['model'])
        self.model = self.model.to(self.device)
        
        # Print model info
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        print(f"Total parameters: {total_params:,}")
        print(f"Trainable parameters: {trainable_params:,}")
    
    def setup_training(self):
        """Setup training components"""
        # Loss function
        self.criterion = HybridLoss(
            main_weight=1.0,
            aux_pixel_weight=0.3,
            aux_compression_weight=0.3,
            uncertainty_weight=0.1
        )
        
        # Optimizer
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.config['training']['learning_rate'],
            weight_decay=self.config['training']['weight_decay']
        )
        
        # Scheduler
        self.scheduler = get_scheduler(
            self.optimizer,
            scheduler_type=self.config['training']['scheduler'],
            num_epochs=self.config['training']['epochs'],
            warmup_epochs=self.config['training']['warmup_epochs']
        )
        
        # Metrics
        self.metrics = DeepfakeMetrics()
        
        # Training state
        self.current_epoch = 0
        self.best_val_auc = 0.0
        self.best_val_acc = 0.0
    
    def setup_logging(self):
        """Setup logging"""
        self.writer = SummaryWriter(log_dir=self.logs_dir)
        
        # Log configuration
        with open(self.logs_dir / 'config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def train_epoch(self) -> dict:
        """Train for one epoch"""
        self.model.train()
        
        total_loss = 0.0
        all_predictions = []
        all_labels = []
        
        pbar = tqdm(self.train_loader, desc=f'Epoch {self.current_epoch+1}/{self.config["training"]["epochs"]}')
        
        for batch_idx, (images, labels) in enumerate(pbar):
            images = images.to(self.device)
            labels = labels.to(self.device).unsqueeze(1)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(images)
            
            # Compute loss
            loss = self.criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            # Update metrics
            total_loss += loss.item()
            
            # Get predictions
            main_probs = torch.sigmoid(outputs['logits'])
            all_predictions.extend(main_probs.cpu().detach().numpy())
            all_labels.extend(labels.cpu().detach().numpy())
            
            # Update progress bar
            pbar.set_postfix({
                'Loss': f'{loss.item():.4f}',
                'LR': f'{self.optimizer.param_groups[0]["lr"]:.6f}'
            })
            
            # Log batch metrics
            if batch_idx % 100 == 0:
                self.writer.add_scalar('Train/BatchLoss', loss.item(), 
                                     self.current_epoch * len(self.train_loader) + batch_idx)
        
        # Compute epoch metrics
        avg_loss = total_loss / len(self.train_loader)
        metrics = self.metrics.compute_metrics(
            np.array(all_predictions).flatten(),
            np.array(all_labels).flatten()
        )
        
        return {
            'loss': avg_loss,
            'accuracy': metrics['accuracy'],
            'auc': metrics['auc'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'f1': metrics['f1']
        }
    
    def validate_epoch(self) -> dict:
        """Validate for one epoch"""
        self.model.eval()
        
        total_loss = 0.0
        all_predictions = []
        all_labels = []
        all_uncertainties = []
        
        with torch.no_grad():
            for images, labels in tqdm(self.val_loader, desc='Validation'):
                images = images.to(self.device)
                labels = labels.to(self.device).unsqueeze(1)
                
                # Forward pass
                outputs = self.model(images)
                
                # Compute loss
                loss = self.criterion(outputs, labels)
                total_loss += loss.item()
                
                # Get predictions
                main_probs = torch.sigmoid(outputs['logits'])
                uncertainties = outputs['uncertainty']
                
                all_predictions.extend(main_probs.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                all_uncertainties.extend(uncertainties.cpu().numpy())
        
        # Compute metrics
        avg_loss = total_loss / len(self.val_loader)
        metrics = self.metrics.compute_metrics(
            np.array(all_predictions).flatten(),
            np.array(all_labels).flatten()
        )
        
        # Add uncertainty metrics
        metrics['avg_uncertainty'] = np.mean(all_uncertainties)
        
        return {
            'loss': avg_loss,
            'accuracy': metrics['accuracy'],
            'auc': metrics['auc'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'f1': metrics['f1'],
            'avg_uncertainty': metrics['avg_uncertainty']
        }
    
    def save_checkpoint(self, metrics: dict, is_best: bool = False):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': self.current_epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'metrics': metrics,
            'config': self.config
        }
        
        # Save regular checkpoint
        checkpoint_path = self.checkpoints_dir / f'checkpoint_epoch_{self.current_epoch}.pth'
        torch.save(checkpoint, checkpoint_path)
        
        # Save best model
        if is_best:
            best_path = self.checkpoints_dir / 'best_model.pth'
            torch.save(checkpoint, best_path)
            print(f"New best model saved with AUC: {metrics['auc']:.4f}")
    
    def load_checkpoint(self, checkpoint_path: str):
        """Load model checkpoint"""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.current_epoch = checkpoint['epoch']
        
        print(f"Loaded checkpoint from epoch {self.current_epoch}")
    
    def train(self):
        """Main training loop"""
        print("Starting training...")
        
        for epoch in range(self.current_epoch, self.config['training']['epochs']):
            self.current_epoch = epoch
            
            # Train epoch
            train_metrics = self.train_epoch()
            
            # Validate epoch
            val_metrics = self.validate_epoch()
            
            # Update scheduler
            self.scheduler.step()
            
            # Log metrics
            self.log_metrics(train_metrics, val_metrics)
            
            # Check if best model
            is_best = val_metrics['auc'] > self.best_val_auc
            if is_best:
                self.best_val_auc = val_metrics['auc']
                self.best_val_acc = val_metrics['accuracy']
            
            # Save checkpoint
            self.save_checkpoint(val_metrics, is_best)
            
            # Print epoch summary
            print(f"Epoch {epoch+1}/{self.config['training']['epochs']}")
            print(f"Train - Loss: {train_metrics['loss']:.4f}, AUC: {train_metrics['auc']:.4f}, Acc: {train_metrics['accuracy']:.4f}")
            print(f"Val   - Loss: {val_metrics['loss']:.4f}, AUC: {val_metrics['auc']:.4f}, Acc: {val_metrics['accuracy']:.4f}")
            print(f"Best Val AUC: {self.best_val_auc:.4f}")
            print("-" * 50)
        
        print("Training completed!")
        print(f"Best validation AUC: {self.best_val_auc:.4f}")
        print(f"Best validation Accuracy: {self.best_val_acc:.4f}")
        
        # Close writer
        self.writer.close()
    
    def log_metrics(self, train_metrics: dict, val_metrics: dict):
        """Log metrics to tensorboard"""
        epoch = self.current_epoch
        
        # Training metrics
        for key, value in train_metrics.items():
            self.writer.add_scalar(f'Train/{key.capitalize()}', value, epoch)
        
        # Validation metrics
        for key, value in val_metrics.items():
            self.writer.add_scalar(f'Val/{key.capitalize()}', value, epoch)
        
        # Learning rate
        self.writer.add_scalar('Train/LearningRate', 
                              self.optimizer.param_groups[0]['lr'], epoch)

def main():
    parser = argparse.ArgumentParser(description='Train Deepfake Detection Model')
    parser.add_argument('--config', type=str, default='config/training_config.json',
                       help='Path to training configuration file')
    parser.add_argument('--resume', type=str, default=None,
                       help='Path to checkpoint to resume from')
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = DeepfakeTrainer(args.config)
    
    # Resume from checkpoint if specified
    if args.resume:
        trainer.load_checkpoint(args.resume)
    
    # Start training
    trainer.train()

if __name__ == '__main__':
    main()
