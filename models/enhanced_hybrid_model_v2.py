import torch
import torch.nn as nn
import torch.nn.functional as F
import json
import numpy as np

class EnhancedHybridFusionModel(nn.Module):
    """
    Enhanced Hybrid Model with GAN + Diffusion Detection
    Combines:
    - LBPH (Classical)
    - Fisherface (Classical)
    - EfficientNet (Deep)
    - GAN Artifact Detector (GAN-specific)
    - Diffusion Forensics Extractor (Diffusion-specific)
    
    With multi-head attention fusion and uncertainty estimation
    """
    
    def __init__(self, config_path="config.json"):
        super().__init__()
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Feature dimensions
        lbph_dim = config['features']['lbph']['grid_x'] * config['features']['lbph']['grid_y'] * 256
        fisherface_dim = config['features']['fisherface']['n_components']
        efficientnet_dim = config['features']['efficientnet']['feature_dim']
        gan_dim = 512
        diffusion_dim = 512
        
        # Project all features to common dimension
        self.lbph_projection = nn.Linear(lbph_dim, 256)
        self.fisherface_projection = nn.Linear(fisherface_dim, 128)
        self.efficientnet_projection = nn.Linear(efficientnet_dim, 512)
        self.gan_projection = nn.Linear(gan_dim, 256)
        self.diffusion_projection = nn.Linear(diffusion_dim, 256)
        
        # Multi-head attention for fusion
        self.num_heads = 4
        total_projected_dim = 256 + 128 + 512 + 256 + 256  # 1408
        
        self.attention = nn.MultiheadAttention(
            embed_dim=512,
            num_heads=self.num_heads,
            batch_first=True,
            dropout=0.2
        )
        
        # Feature normalization
        self.layer_norm = nn.LayerNorm(512)
        
        # Classification head
        hidden_dims = config['model']['hidden_dims']
        layers = []
        prev_dim = 512
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3),
                nn.BatchNorm1d(hidden_dim)
            ])
            prev_dim = hidden_dim
        
        # Final layer
        layers.append(nn.Linear(prev_dim, 2))
        self.classifier = nn.Sequential(*layers)
        
        # Uncertainty estimation layers
        # Uncertainty head operates on the fused feature vector (512-dim)
        self.uncertainty_head = nn.Sequential(
            nn.Linear(512, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 1),
            nn.Softplus()
        )
        
        # Initialization
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """Initialize weights"""
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                nn.init.constant_(module.bias, 0)
        elif isinstance(module, nn.BatchNorm1d):
            nn.init.constant_(module.weight, 1)
            nn.init.constant_(module.bias, 0)
    
    def forward(self, lbph_features, fisherface_features, efficientnet_features, 
                gan_features, diffusion_features, dropout_enabled=False):
        """Forward pass with all feature streams"""
        
        # Project features
        lbph_proj = F.relu(self.lbph_projection(lbph_features))
        fisherface_proj = F.relu(self.fisherface_projection(fisherface_features))
        efficientnet_proj = F.relu(self.efficientnet_projection(efficientnet_features))
        gan_proj = F.relu(self.gan_projection(gan_features))
        diffusion_proj = F.relu(self.diffusion_projection(diffusion_features))
        
        # Prepare projected features for attention (some projections have different dims)
        batch_size = lbph_proj.size(0)
        
        # Pad features to same dimension for attention
        features_padded = []
        for feat in [efficientnet_proj, gan_proj, diffusion_proj]:
            if feat.size(1) < 512:
                padding = nn.functional.pad(feat, (0, 512 - feat.size(1)))
            else:
                padding = feat[:, :512]
            features_padded.append(padding)
        
        features_stacked = torch.stack(features_padded, dim=1)  # [batch_size, 3, 512]
        
        # Multi-head attention
        attn_out, attn_weights = self.attention(features_stacked, features_stacked, features_stacked)
        
        # Average attention output
        fused_features = torch.mean(attn_out, dim=1)  # [batch_size, 512]
        fused_features = self.layer_norm(fused_features)
        
        # Optional Monte Carlo dropout for uncertainty
        if dropout_enabled and self.training:
            features_with_dropout = F.dropout(fused_features, p=0.2, training=True)
        else:
            features_with_dropout = fused_features
        
        # Classification
        logits = self.classifier(features_with_dropout)
        
        # Uncertainty estimation
        uncertainty = self.uncertainty_head(features_with_dropout)
        
        return logits, uncertainty
    
    def predict_proba(self, lbph_features, fisherface_features, efficientnet_features,
                      gan_features, diffusion_features, num_mc_samples=5):
        """Get prediction probabilities with uncertainty"""
        self.eval()
        
        all_probs = []
        all_uncertainties = []
        
        with torch.no_grad():
            for _ in range(num_mc_samples):
                logits, uncertainty = self.forward(
                    lbph_features, fisherface_features, efficientnet_features,
                    gan_features, diffusion_features, dropout_enabled=True
                )
                
                probs = F.softmax(logits, dim=1)
                all_probs.append(probs)
                all_uncertainties.append(uncertainty)
        
        # Average predictions
        mean_probs = torch.mean(torch.stack(all_probs), dim=0)
        mean_uncertainty = torch.mean(torch.stack(all_uncertainties), dim=0)
        
        return mean_probs, mean_uncertainty
    
    def predict(self, lbph_features, fisherface_features, efficientnet_features,
                gan_features, diffusion_features, threshold=0.5):
        """Get binary predictions"""
        probs, uncertainty = self.predict_proba(
            lbph_features, fisherface_features, efficientnet_features,
            gan_features, diffusion_features
        )
        
        fake_prob = probs[:, 1]  # Probability of being fake
        predictions = (fake_prob > threshold).long()
        
        return predictions, fake_prob, uncertainty

if __name__ == "__main__":
    model = EnhancedHybridFusionModel()
    print(f"Enhanced Hybrid Model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Test forward pass
    batch_size = 4
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    lbph_dummy = torch.randn(batch_size, 256 * 8 * 8).to(device)
    fisherface_dummy = torch.randn(batch_size, 100).to(device)
    efficientnet_dummy = torch.randn(batch_size, 1792).to(device)
    gan_dummy = torch.randn(batch_size, 512).to(device)
    diffusion_dummy = torch.randn(batch_size, 512).to(device)
    
    logits, uncertainty = model(lbph_dummy, fisherface_dummy, efficientnet_dummy, gan_dummy, diffusion_dummy)
    print(f"Output shape: {logits.shape}")
    print(f"Uncertainty shape: {uncertainty.shape}")
