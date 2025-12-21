import torch
import torch.nn as nn
import torch.nn.functional as F
from efficientnet_pytorch import EfficientNet
import timm
import numpy as np
from typing import Dict, List, Tuple, Optional
import cv2
from .pixel_features import PixelFeatureExtractor
from .compression_detector import CompressionFeatureExtractor

class MultiScaleFeatureExtractor(nn.Module):
    """Multi-scale feature extraction for different levels of analysis"""
    
    def __init__(self, input_channels: int = 3):
        super().__init__()
        
        # Different scales for analysis
        self.scales = [1.0, 0.75, 0.5]
        
        # Feature extractors for each scale
        self.scale_extractors = nn.ModuleList([
            nn.Sequential(
                nn.Conv2d(input_channels, 64, 3, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU(inplace=True),
                nn.Conv2d(64, 128, 3, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(inplace=True),
                nn.AdaptiveAvgPool2d((8, 8))
            ) for _ in self.scales
        ])
        
        # Feature fusion
        self.fusion = nn.Sequential(
            nn.Linear(128 * 64 * len(self.scales), 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 256)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.size(0)
        scale_features = []
        
        for i, scale in enumerate(self.scales):
            if scale != 1.0:
                # Resize input
                new_size = (int(x.size(2) * scale), int(x.size(3) * scale))
                scaled_x = F.interpolate(x, size=new_size, mode='bilinear', align_corners=False)
            else:
                scaled_x = x
            
            # Extract features at this scale
            features = self.scale_extractors[i](scaled_x)
            features = features.view(batch_size, -1)
            scale_features.append(features)
        
        # Concatenate all scale features
        combined = torch.cat(scale_features, dim=1)
        output = self.fusion(combined)
        
        return output

class AttentionFusion(nn.Module):
    """Attention-based feature fusion mechanism"""
    
    def __init__(self, feature_dims: List[int], output_dim: int = 512):
        super().__init__()
        
        self.feature_dims = feature_dims
        self.output_dim = output_dim
        
        # Individual feature projections
        self.feature_projections = nn.ModuleList([
            nn.Linear(dim, output_dim) for dim in feature_dims
        ])
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=output_dim,
            num_heads=8,
            dropout=0.1,
            batch_first=True
        )
        
        # Final fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(output_dim, output_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(output_dim, output_dim)
        )
    
    def forward(self, features: List[torch.Tensor]) -> torch.Tensor:
        # Project all features to same dimension
        projected_features = []
        for i, feat in enumerate(features):
            projected = self.feature_projections[i](feat)
            projected_features.append(projected.unsqueeze(1))  # Add sequence dimension
        
        # Stack features for attention
        stacked_features = torch.cat(projected_features, dim=1)  # [batch, num_features, dim]
        
        # Apply self-attention
        attended_features, attention_weights = self.attention(
            stacked_features, stacked_features, stacked_features
        )
        
        # Global average pooling over feature dimension
        fused_features = torch.mean(attended_features, dim=1)
        
        # Final fusion
        output = self.fusion(fused_features)
        
        return output

class ClassicalFeatureExtractor(nn.Module):
    """Classical computer vision features (LBP, Fisherface, etc.)"""
    
    def __init__(self, feature_dim: int = 256):
        super().__init__()
        
        self.feature_dim = feature_dim
        
        # Feature processing network
        self.feature_processor = nn.Sequential(
            nn.Linear(200, 512),  # Assuming ~200 classical features
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, feature_dim),
            nn.ReLU(inplace=True),
            nn.Linear(feature_dim, feature_dim)
        )
    
    def extract_classical_features(self, image: np.ndarray) -> np.ndarray:
        """Extract classical CV features"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        features = []
        
        # 1. Local Binary Pattern (LBP)
        lbp_features = self._extract_lbp_features(gray)
        features.extend(lbp_features)
        
        # 2. Histogram of Oriented Gradients (HOG)
        hog_features = self._extract_hog_features(gray)
        features.extend(hog_features)
        
        # 3. Haralick texture features
        haralick_features = self._extract_haralick_features(gray)
        features.extend(haralick_features)
        
        # 4. Statistical features
        stat_features = self._extract_statistical_features(gray)
        features.extend(stat_features)
        
        # Pad or truncate to fixed size
        if len(features) > 200:
            features = features[:200]
        else:
            features.extend([0.0] * (200 - len(features)))
        
        return np.array(features, dtype=np.float32)
    
    def _extract_lbp_features(self, gray: np.ndarray) -> List[float]:
        """Extract LBP features"""
        from skimage.feature import local_binary_pattern
        
        features = []
        
        # Multi-radius LBP
        for radius in [1, 2, 3]:
            n_points = 8 * radius
            lbp = local_binary_pattern(gray, n_points, radius, method='uniform')
            
            # LBP histogram
            hist, _ = np.histogram(lbp.ravel(), bins=n_points + 2, 
                                 range=(0, n_points + 2), density=True)
            features.extend(hist[:10])  # Take first 10 bins
        
        return features
    
    def _extract_hog_features(self, gray: np.ndarray) -> List[float]:
        """Extract HOG features"""
        from skimage.feature import hog
        
        try:
            hog_features = hog(gray, orientations=9, pixels_per_cell=(8, 8),
                              cells_per_block=(2, 2), block_norm='L2-Hys',
                              feature_vector=True)
            # Take first 50 features
            return hog_features[:50].tolist()
        except:
            return [0.0] * 50
    
    def _extract_haralick_features(self, gray: np.ndarray) -> List[float]:
        """Extract Haralick texture features"""
        from skimage.feature import graycomatrix, graycoprops
        
        try:
            # Reduce image size for faster computation
            small_gray = cv2.resize(gray, (64, 64))
            
            # GLCM
            glcm = graycomatrix(small_gray, [1], [0, 45, 90, 135], 
                              levels=256, symmetric=True, normed=True)
            
            # Haralick features
            features = []
            properties = ['contrast', 'dissimilarity', 'homogeneity', 'energy']
            
            for prop in properties:
                values = graycoprops(glcm, prop)
                features.extend(values.flatten()[:4])  # Take first 4 values
            
            return features
        except:
            return [0.0] * 16
    
    def _extract_statistical_features(self, gray: np.ndarray) -> List[float]:
        """Extract statistical features"""
        features = []
        
        # Basic statistics
        features.extend([
            np.mean(gray), np.std(gray), np.var(gray),
            np.min(gray), np.max(gray),
            np.percentile(gray, 25), np.percentile(gray, 75),
            np.median(gray)
        ])
        
        # Gradient statistics
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        features.extend([
            np.mean(magnitude), np.std(magnitude),
            np.percentile(magnitude, 90)
        ])
        
        return features
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.size(0)
        classical_features = []
        
        for i in range(batch_size):
            # Convert to numpy
            img_np = x[i].permute(1, 2, 0).cpu().numpy()
            img_np = (img_np * 255).astype(np.uint8)
            
            # Extract classical features
            features = self.extract_classical_features(img_np)
            classical_features.append(features)
        
        # Convert to tensor
        classical_features = torch.tensor(
            np.array(classical_features),
            dtype=torch.float32,
            device=x.device
        )
        
        # Process through network
        output = self.feature_processor(classical_features)
        
        return output

class HybridDeepfakeDetector(nn.Module):
    """Hybrid deepfake detection model combining multiple approaches"""
    
    def __init__(self, 
                 backbone: str = 'efficientnet-b4',
                 num_classes: int = 1,
                 pretrained: bool = True,
                 dropout: float = 0.3):
        super().__init__()
        
        self.backbone_name = backbone
        self.num_classes = num_classes
        
        # 1. Deep learning backbone
        if 'efficientnet' in backbone:
            self.backbone = EfficientNet.from_pretrained(backbone) if pretrained else EfficientNet.from_name(backbone)
            backbone_features = self.backbone._fc.in_features
            self.backbone._fc = nn.Identity()  # Remove final layer
        else:
            # Use timm for other architectures
            self.backbone = timm.create_model(backbone, pretrained=pretrained, num_classes=0)
            backbone_features = self.backbone.num_features
        
        # 2. Specialized feature extractors
        self.pixel_extractor = PixelFeatureExtractor(feature_dim=512)
        self.compression_extractor = CompressionFeatureExtractor(feature_dim=256)
        self.classical_extractor = ClassicalFeatureExtractor(feature_dim=256)
        self.multiscale_extractor = MultiScaleFeatureExtractor()
        
        # 3. Attention-based fusion
        feature_dims = [backbone_features, 512, 256, 256, 256]  # Dimensions of each feature type
        self.attention_fusion = AttentionFusion(feature_dims, output_dim=512)
        
        # 4. Final classification layers
        self.classifier = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes)
        )
        
        # 5. Auxiliary classifiers for multi-task learning
        self.aux_pixel_classifier = nn.Linear(512, num_classes)
        self.aux_compression_classifier = nn.Linear(256, num_classes)
        
        # 6. Uncertainty estimation
        self.uncertainty_head = nn.Sequential(
            nn.Linear(512, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 1),
            nn.Softplus()  # Ensure positive uncertainty
        )
    
    def forward(self, x: torch.Tensor, return_features: bool = False) -> Dict[str, torch.Tensor]:
        batch_size = x.size(0)
        
        # 1. Extract features from different modules
        backbone_features = self.backbone(x)
        pixel_features = self.pixel_extractor(x)
        compression_features = self.compression_extractor(x)
        classical_features = self.classical_extractor(x)
        multiscale_features = self.multiscale_extractor(x)
        
        # 2. Fuse features using attention
        all_features = [
            backbone_features,
            pixel_features,
            compression_features,
            classical_features,
            multiscale_features
        ]
        
        fused_features = self.attention_fusion(all_features)
        
        # 3. Main classification
        main_logits = self.classifier(fused_features)
        
        # 4. Auxiliary classifications
        aux_pixel_logits = self.aux_pixel_classifier(pixel_features)
        aux_compression_logits = self.aux_compression_classifier(compression_features)
        
        # 5. Uncertainty estimation
        uncertainty = self.uncertainty_head(fused_features)
        
        outputs = {
            'logits': main_logits,
            'aux_pixel_logits': aux_pixel_logits,
            'aux_compression_logits': aux_compression_logits,
            'uncertainty': uncertainty
        }
        
        if return_features:
            outputs['features'] = {
                'backbone': backbone_features,
                'pixel': pixel_features,
                'compression': compression_features,
                'classical': classical_features,
                'multiscale': multiscale_features,
                'fused': fused_features
            }
        
        return outputs
    
    def predict_with_uncertainty(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Predict with uncertainty estimation"""
        self.eval()
        
        with torch.no_grad():
            outputs = self.forward(x)
            
            # Main prediction
            logits = outputs['logits']
            probs = torch.sigmoid(logits)
            
            # Uncertainty
            uncertainty = outputs['uncertainty']
            
            # Ensemble prediction (average of main and auxiliary)
            aux_pixel_probs = torch.sigmoid(outputs['aux_pixel_logits'])
            aux_compression_probs = torch.sigmoid(outputs['aux_compression_logits'])
            
            ensemble_probs = (probs + aux_pixel_probs + aux_compression_probs) / 3
            
        return ensemble_probs, probs, uncertainty
    
    def get_attention_weights(self, x: torch.Tensor) -> torch.Tensor:
        """Get attention weights for feature importance analysis"""
        # This would require modifying the attention mechanism to return weights
        # For now, return dummy weights
        batch_size = x.size(0)
        return torch.ones(batch_size, 5) / 5  # Equal weights for 5 feature types

class EnsembleDeepfakeDetector(nn.Module):
    """Ensemble of multiple hybrid models for improved performance"""
    
    def __init__(self, 
                 model_configs: List[Dict],
                 ensemble_method: str = 'average'):
        super().__init__()
        
        self.ensemble_method = ensemble_method
        
        # Create multiple models
        self.models = nn.ModuleList()
        for config in model_configs:
            model = HybridDeepfakeDetector(**config)
            self.models.append(model)
        
        # Ensemble fusion (if using learned ensemble)
        if ensemble_method == 'learned':
            self.ensemble_fusion = nn.Sequential(
                nn.Linear(len(model_configs), 64),
                nn.ReLU(inplace=True),
                nn.Linear(64, 1),
                nn.Softmax(dim=1)
            )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        predictions = []
        uncertainties = []
        
        for model in self.models:
            outputs = model(x)
            predictions.append(torch.sigmoid(outputs['logits']))
            uncertainties.append(outputs['uncertainty'])
        
        # Stack predictions
        stacked_preds = torch.stack(predictions, dim=-1)  # [batch, 1, num_models]
        stacked_uncertainties = torch.stack(uncertainties, dim=-1)
        
        if self.ensemble_method == 'average':
            # Simple average
            ensemble_pred = torch.mean(stacked_preds, dim=-1)
            ensemble_uncertainty = torch.mean(stacked_uncertainties, dim=-1)
            
        elif self.ensemble_method == 'weighted':
            # Inverse uncertainty weighting
            weights = 1.0 / (stacked_uncertainties + 1e-8)
            weights = weights / torch.sum(weights, dim=-1, keepdim=True)
            
            ensemble_pred = torch.sum(stacked_preds * weights, dim=-1)
            ensemble_uncertainty = torch.sum(stacked_uncertainties * weights, dim=-1)
            
        elif self.ensemble_method == 'learned':
            # Learned ensemble weights
            weights = self.ensemble_fusion(stacked_preds.squeeze(1))
            ensemble_pred = torch.sum(stacked_preds * weights.unsqueeze(1), dim=-1)
            ensemble_uncertainty = torch.sum(stacked_uncertainties * weights, dim=-1)
        
        return {
            'logits': torch.logit(ensemble_pred + 1e-8),  # Convert back to logits
            'predictions': ensemble_pred,
            'uncertainty': ensemble_uncertainty,
            'individual_predictions': stacked_preds,
            'individual_uncertainties': stacked_uncertainties
        }

def create_hybrid_model(config: Dict) -> HybridDeepfakeDetector:
    """Factory function to create hybrid model from config"""
    return HybridDeepfakeDetector(
        backbone=config.get('backbone', 'efficientnet-b4'),
        num_classes=config.get('num_classes', 1),
        pretrained=config.get('pretrained', True),
        dropout=config.get('dropout', 0.3)
    )

def create_ensemble_model(configs: List[Dict]) -> EnsembleDeepfakeDetector:
    """Factory function to create ensemble model"""
    return EnsembleDeepfakeDetector(
        model_configs=configs,
        ensemble_method='weighted'  # Use uncertainty-weighted ensemble
    )

# Example usage and model configurations
SINGLE_MODEL_CONFIG = {
    'backbone': 'efficientnet-b4',
    'num_classes': 1,
    'pretrained': True,
    'dropout': 0.3
}

ENSEMBLE_CONFIGS = [
    {'backbone': 'efficientnet-b4', 'num_classes': 1, 'pretrained': True, 'dropout': 0.3},
    {'backbone': 'efficientnet-b3', 'num_classes': 1, 'pretrained': True, 'dropout': 0.2},
    {'backbone': 'resnet50', 'num_classes': 1, 'pretrained': True, 'dropout': 0.4},
]
