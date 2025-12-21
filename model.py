import torch
import torch.nn as nn
import torch.nn.functional as F
import json
import numpy as np

class HybridFusionModel(nn.Module):
    def __init__(self, config_path="config.json"):
        super().__init__()
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Feature dimensions
        lbph_dim = config['features']['lbph']['grid_x'] * config['features']['lbph']['grid_y'] * 256
        fisherface_dim = config['features']['fisherface']['n_components']
        efficientnet_dim = config['features']['efficientnet']['feature_dim']
        
        # Fusion configuration
        self.fusion_method = config['model']['fusion_method']
        hidden_dims = config['model']['hidden_dims']
        dropout = config['model']['dropout']
        activation = config['model']['activation']
        
        # Feature projections (optional dimensionality reduction)
        self.lbph_projection = nn.Linear(lbph_dim, 256)
        self.fisherface_projection = nn.Linear(fisherface_dim, 128)
        self.efficientnet_projection = nn.Linear(efficientnet_dim, 512)
        
        # Fusion layer
        if self.fusion_method == "concatenate":
            fusion_dim = 256 + 128 + 512  # Sum of projected dimensions
        elif self.fusion_method == "attention":
            fusion_dim = 512  # Fixed dimension for attention
            self.attention_weights = nn.Linear(256 + 128 + 512, 3)
        else:
            raise ValueError(f"Unknown fusion method: {self.fusion_method}")
        
        # Classification head
        layers = []
        prev_dim = fusion_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                self._get_activation(activation),
                nn.Dropout(dropout),
                nn.BatchNorm1d(hidden_dim)
            ])
            prev_dim = hidden_dim
        
        # Final classification layer
        layers.append(nn.Linear(prev_dim, 2))  # Binary classification
        
        self.classifier = nn.Sequential(*layers)
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _get_activation(self, activation):
        """Get activation function"""
        if activation == "relu":
            return nn.ReLU(inplace=True)
        elif activation == "gelu":
            return nn.GELU()
        elif activation == "swish":
            return nn.SiLU(inplace=True)
        else:
            return nn.ReLU(inplace=True)
    
    def _init_weights(self, module):
        """Initialize weights"""
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                nn.init.constant_(module.bias, 0)
        elif isinstance(module, nn.BatchNorm1d):
            nn.init.constant_(module.weight, 1)
            nn.init.constant_(module.bias, 0)
    
    def forward(self, lbph_features, fisherface_features, efficientnet_features):
        """Forward pass"""
        # Project features
        lbph_proj = F.relu(self.lbph_projection(lbph_features))
        fisherface_proj = F.relu(self.fisherface_projection(fisherface_features))
        efficientnet_proj = F.relu(self.efficientnet_projection(efficientnet_features))
        
        # Fusion
        if self.fusion_method == "concatenate":
            fused_features = torch.cat([lbph_proj, fisherface_proj, efficientnet_proj], dim=1)
        
        elif self.fusion_method == "attention":
            # Concatenate for attention computation
            concat_features = torch.cat([lbph_proj, fisherface_proj, efficientnet_proj], dim=1)
            
            # Compute attention weights
            attention_scores = F.softmax(self.attention_weights(concat_features), dim=1)
            
            # Apply attention
            features_stack = torch.stack([
                F.adaptive_avg_pool1d(lbph_proj.unsqueeze(1), 512).squeeze(1),
                F.adaptive_avg_pool1d(fisherface_proj.unsqueeze(1), 512).squeeze(1),
                F.adaptive_avg_pool1d(efficientnet_proj.unsqueeze(1), 512).squeeze(1)
            ], dim=2)  # [batch, 512, 3]
            
            # Weighted sum
            fused_features = torch.sum(features_stack * attention_scores.unsqueeze(1), dim=2)
        
        # Classification
        logits = self.classifier(fused_features)
        
        return logits
    
    def predict_proba(self, lbph_features, fisherface_features, efficientnet_features):
        """Get prediction probabilities"""
        self.eval()
        with torch.no_grad():
            logits = self.forward(lbph_features, fisherface_features, efficientnet_features)
            probabilities = F.softmax(logits, dim=1)
        return probabilities
    
    def predict(self, lbph_features, fisherface_features, efficientnet_features, threshold=0.5):
        """Get binary predictions"""
        probabilities = self.predict_proba(lbph_features, fisherface_features, efficientnet_features)
        fake_prob = probabilities[:, 1]  # Probability of being fake
        predictions = (fake_prob > threshold).long()
        return predictions, fake_prob

class FocalLoss(nn.Module):
    """Focal Loss for handling class imbalance"""
    def __init__(self, alpha=1, gamma=2, reduction='mean'):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
    
    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss

class ModelTrainer:
    def __init__(self, model, config_path="config.json"):
        self.model = model
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Training configuration
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # Loss function
        self.criterion = FocalLoss(alpha=1, gamma=2)
        
        # Optimizer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config['training']['learning_rate'],
            weight_decay=self.config['training']['weight_decay']
        )
        
        # Scheduler
        self.scheduler = None
        if self.config['training']['scheduler'] == 'cosine':
            self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer, 
                T_max=self.config['training']['epochs']
            )
        elif self.config['training']['scheduler'] == 'step':
            self.scheduler = torch.optim.lr_scheduler.StepLR(
                self.optimizer, 
                step_size=30, 
                gamma=0.1
            )
        
        # Early stopping
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        self.patience = self.config['training']['early_stopping_patience']
    
    def train_epoch(self, train_loader):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch in train_loader:
            lbph_features = batch['lbph'].to(self.device)
            fisherface_features = batch['fisherface'].to(self.device)
            efficientnet_features = batch['efficientnet'].to(self.device)
            labels = batch['label'].to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            logits = self.model(lbph_features, fisherface_features, efficientnet_features)
            loss = self.criterion(logits, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            total_loss += loss.item()
            _, predicted = torch.max(logits.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(train_loader)
        accuracy = 100 * correct / total
        
        return avg_loss, accuracy
    
    def validate(self, val_loader):
        """Validate model"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in val_loader:
                lbph_features = batch['lbph'].to(self.device)
                fisherface_features = batch['fisherface'].to(self.device)
                efficientnet_features = batch['efficientnet'].to(self.device)
                labels = batch['label'].to(self.device)
                
                logits = self.model(lbph_features, fisherface_features, efficientnet_features)
                loss = self.criterion(logits, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(logits.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = 100 * correct / total
        
        return avg_loss, accuracy
    
    def should_stop_early(self, val_loss):
        """Check if training should stop early"""
        if val_loss < self.best_val_loss:
            self.best_val_loss = val_loss
            self.patience_counter = 0
            return False
        else:
            self.patience_counter += 1
            return self.patience_counter >= self.patience

if __name__ == "__main__":
    # Test model creation
    model = HybridFusionModel()
    print(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Test forward pass
    batch_size = 4
    lbph_dummy = torch.randn(batch_size, 256 * 8 * 8)  # LBPH features
    fisherface_dummy = torch.randn(batch_size, 100)     # Fisherface features
    efficientnet_dummy = torch.randn(batch_size, 1792) # EfficientNet features
    
    logits = model(lbph_dummy, fisherface_dummy, efficientnet_dummy)
    print(f"Output shape: {logits.shape}")
