import torch
import torch.nn as nn
import torch.nn.functional as F
from efficientnet_pytorch import EfficientNet
import timm
import numpy as np
from typing import Dict, List, Tuple, Optional
import math
from .advanced_features import AdvancedFeatureExtractor
from .pixel_features import PixelFeatureExtractor
from .compression_detector import CompressionFeatureExtractor

class VisionTransformerBlock(nn.Module):
    """Vision Transformer block for spatial attention"""
    
    def __init__(self, dim: int, num_heads: int = 8, mlp_ratio: float = 4.0, dropout: float = 0.1):
        super().__init__()
        
        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.norm2 = nn.LayerNorm(dim)
        
        mlp_hidden_dim = int(dim * mlp_ratio)
        self.mlp = nn.Sequential(
            nn.Linear(dim, mlp_hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(mlp_hidden_dim, dim),
            nn.Dropout(dropout)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Self-attention
        x_norm = self.norm1(x)
        attn_out, _ = self.attn(x_norm, x_norm, x_norm)
        x = x + attn_out
        
        # MLP
        x = x + self.mlp(self.norm2(x))
        
        return x

class CrossAttentionFusion(nn.Module):
    """Cross-attention between different feature modalities"""
    
    def __init__(self, feature_dims: List[int], output_dim: int = 512, num_heads: int = 8):
        super().__init__()
        
        self.feature_dims = feature_dims
        self.output_dim = output_dim
        self.num_heads = num_heads
        
        # Project all features to same dimension
        self.feature_projections = nn.ModuleList([
            nn.Sequential(
                nn.Linear(dim, output_dim),
                nn.LayerNorm(output_dim),
                nn.ReLU(inplace=True)
            ) for dim in feature_dims
        ])
        
        # Cross-attention layers
        self.cross_attention_layers = nn.ModuleList([
            nn.MultiheadAttention(output_dim, num_heads, dropout=0.1, batch_first=True)
            for _ in range(len(feature_dims))
        ])
        
        # Self-attention for final fusion
        self.self_attention = nn.MultiheadAttention(output_dim, num_heads, dropout=0.1, batch_first=True)
        
        # Final fusion network
        self.fusion_network = nn.Sequential(
            nn.Linear(output_dim * len(feature_dims), output_dim),
            nn.LayerNorm(output_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(output_dim, output_dim)
        )
    
    def forward(self, features: List[torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]:
        batch_size = features[0].size(0)
        
        # Project all features to same dimension
        projected_features = []
        for i, feat in enumerate(features):
            projected = self.feature_projections[i](feat)
            projected_features.append(projected.unsqueeze(1))  # Add sequence dimension
        
        # Cross-attention between modalities
        attended_features = []
        for i, query_feat in enumerate(projected_features):
            # Use current feature as query, others as key/value
            key_value_feats = [feat for j, feat in enumerate(projected_features) if j != i]
            if key_value_feats:
                key_value = torch.cat(key_value_feats, dim=1)
                attended, attention_weights = self.cross_attention_layers[i](
                    query_feat, key_value, key_value
                )
                attended_features.append(attended.squeeze(1))
            else:
                attended_features.append(query_feat.squeeze(1))
        
        # Concatenate attended features
        concatenated = torch.cat(attended_features, dim=1)
        
        # Final fusion
        fused_features = self.fusion_network(concatenated)
        
        # Self-attention for global context
        fused_features_seq = fused_features.unsqueeze(1)
        final_features, final_attention = self.self_attention(
            fused_features_seq, fused_features_seq, fused_features_seq
        )
        
        return final_features.squeeze(1), final_attention

class MetaLearningAdapter(nn.Module):
    """Meta-learning adapter for quick adaptation to new deepfake techniques"""
    
    def __init__(self, feature_dim: int, adaptation_steps: int = 5):
        super().__init__()
        
        self.feature_dim = feature_dim
        self.adaptation_steps = adaptation_steps
        
        # Meta-parameters for adaptation
        self.meta_params = nn.ParameterDict({
            'alpha': nn.Parameter(torch.ones(feature_dim) * 0.01),
            'beta': nn.Parameter(torch.zeros(feature_dim))
        })
        
        # Adaptation network
        self.adaptation_network = nn.Sequential(
            nn.Linear(feature_dim, feature_dim // 2),
            nn.ReLU(inplace=True),
            nn.Linear(feature_dim // 2, feature_dim),
            nn.Tanh()
        )
    
    def forward(self, features: torch.Tensor, support_set: Optional[torch.Tensor] = None) -> torch.Tensor:
        if support_set is not None and self.training:
            adapted_features = self.adapt_features(features, support_set)
        else:
            # Standard forward pass
            adapted_features = features
        
        # Apply meta-parameters
        adapted_features = self.meta_params['alpha'] * adapted_features + self.meta_params['beta']
        
        # Adaptation network
        adaptation = self.adaptation_network(adapted_features)
        final_features = adapted_features + adaptation
        
        return final_features
    
    def adapt_features(self, features: torch.Tensor, support_set: torch.Tensor) -> torch.Tensor:
        """Adapt features based on support set"""
        # Compute prototype from support set
        prototype = torch.mean(support_set, dim=0, keepdim=True)
        
        # Compute adaptation based on distance to prototype
        distance = F.cosine_similarity(features, prototype, dim=1, keepdim=True)
        adaptation_weight = torch.sigmoid(distance)
        
        # Weighted combination
        adapted = adaptation_weight * features + (1 - adaptation_weight) * prototype
        
        return adapted

class UncertaintyEstimator(nn.Module):
    """Advanced uncertainty estimation with multiple methods"""
    
    def __init__(self, feature_dim: int, num_samples: int = 10):
        super().__init__()
        
        self.feature_dim = feature_dim
        self.num_samples = num_samples
        
        # Aleatoric uncertainty (data uncertainty)
        self.aleatoric_head = nn.Sequential(
            nn.Linear(feature_dim, feature_dim // 2),
            nn.ReLU(inplace=True),
            nn.Linear(feature_dim // 2, 1),
            nn.Softplus()
        )
        
        # Epistemic uncertainty (model uncertainty) via dropout
        self.epistemic_layers = nn.Sequential(
            nn.Linear(feature_dim, feature_dim // 2),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(feature_dim // 2, feature_dim // 4),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(feature_dim // 4, 1)
        )
    
    def forward(self, features: torch.Tensor, training: bool = True) -> Dict[str, torch.Tensor]:
        # Aleatoric uncertainty
        aleatoric = self.aleatoric_head(features)
        
        if training:
            # Single forward pass during training
            epistemic_logits = self.epistemic_layers(features)
            epistemic = torch.zeros_like(aleatoric)
        else:
            # Monte Carlo dropout for epistemic uncertainty
            epistemic_samples = []
            for _ in range(self.num_samples):
                sample = self.epistemic_layers(features)
                epistemic_samples.append(sample)
            
            epistemic_samples = torch.stack(epistemic_samples, dim=0)
            epistemic_logits = torch.mean(epistemic_samples, dim=0)
            epistemic = torch.var(epistemic_samples, dim=0)
        
        # Total uncertainty
        total_uncertainty = aleatoric + epistemic
        
        return {
            'aleatoric': aleatoric,
            'epistemic': epistemic,
            'total': total_uncertainty,
            'logits': epistemic_logits
        }

class EnhancedHybridModel(nn.Module):
    """Enhanced hybrid model with Vision Transformer, cross-attention, and meta-learning"""
    
    def __init__(self, 
                 backbone: str = 'efficientnet-b4',
                 num_classes: int = 1,
                 pretrained: bool = True,
                 dropout: float = 0.3,
                 use_transformer: bool = True,
                 use_meta_learning: bool = True):
        super().__init__()
        
        self.backbone_name = backbone
        self.num_classes = num_classes
        self.use_transformer = use_transformer
        self.use_meta_learning = use_meta_learning
        
        if 'efficientnet' in backbone:
            self.backbone = EfficientNet.from_pretrained(backbone) if pretrained else EfficientNet.from_name(backbone)
            backbone_features = self.backbone._fc.in_features
            self.backbone._fc = nn.Identity()
        else:
            self.backbone = timm.create_model(backbone, pretrained=pretrained, num_classes=0)
            backbone_features = self.backbone.num_features
        
        self.advanced_extractor = AdvancedFeatureExtractor()
        self.pixel_extractor = PixelFeatureExtractor(feature_dim=512)
        self.compression_extractor = CompressionFeatureExtractor(feature_dim=256)
        
        if use_transformer:
            self.transformer_blocks = nn.ModuleList([
                VisionTransformerBlock(backbone_features, num_heads=8, dropout=dropout)
                for _ in range(2)
            ])
            
            # Positional encoding for transformer
            self.pos_encoding = nn.Parameter(torch.randn(1, 196, backbone_features))  # 14x14 patches
        
        feature_dims = [backbone_features, 512, 256, 200]  # Advanced features ~200 dim
        self.cross_attention_fusion = CrossAttentionFusion(feature_dims, output_dim=512)
        
        if use_meta_learning:
            self.meta_adapter = MetaLearningAdapter(512)
        
        self.uncertainty_estimator = UncertaintyEstimator(512)
        
        self.main_classifier = nn.Sequential(
            nn.Linear(512, 256),
            nn.LayerNorm(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes)
        )
        
        self.aux_pixel_classifier = nn.Linear(512, num_classes)
        self.aux_compression_classifier = nn.Linear(256, num_classes)
        self.aux_temporal_classifier = nn.Linear(512, num_classes)  # For temporal consistency
        
        self.calibration_layer = nn.Sequential(
            nn.Linear(num_classes, num_classes),
            nn.Sigmoid()
        )
    
    def extract_backbone_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract features from backbone with optional transformer enhancement"""
        features = self.backbone(x)
        
        if self.use_transformer and hasattr(self, 'transformer_blocks'):
            batch_size = features.size(0)
            
            # Reshape for transformer (assume features are flattened)
            if len(features.shape) == 2:
                # Add positional encoding
                seq_len = min(features.size(1), self.pos_encoding.size(1))
                features_seq = features[:, :seq_len].unsqueeze(1)
                features_seq = features_seq + self.pos_encoding[:, :seq_len, :features.size(1)]
                
                # Apply transformer blocks
                for transformer_block in self.transformer_blocks:
                    features_seq = transformer_block(features_seq)
                
                # Global average pooling
                features = torch.mean(features_seq, dim=1)
        
        return features
    
    def forward(self, x: torch.Tensor, 
                support_set: Optional[torch.Tensor] = None,
                return_features: bool = False,
                return_attention: bool = False) -> Dict[str, torch.Tensor]:
        
        batch_size = x.size(0)
        
        backbone_features = self.extract_backbone_features(x)
        
        pixel_features = self.pixel_extractor(x)
        compression_features = self.compression_extractor(x)
        
        # Extract advanced features (frequency, face geometry, etc.)
        advanced_features_list = []
        for i in range(batch_size):
            img_np = x[i].permute(1, 2, 0).cpu().numpy()
            img_np = (img_np * 255).astype(np.uint8)
            
            adv_features = self.advanced_extractor.extract_comprehensive_features(img_np)
            # Concatenate all advanced features
            all_adv_features = np.concatenate([
                adv_features.get('frequency_advanced', np.zeros(20))[:20],
                adv_features.get('face_geometry', np.zeros(11))[:11],
                adv_features.get('micro_expressions', np.zeros(21))[:21],
                adv_features.get('skin_texture', np.zeros(4))[:4],
                adv_features.get('multi_resolution', np.zeros(16))[:16],
                adv_features.get('compression_advanced', np.zeros(4))[:4]
            ])
            
            # Pad or truncate to fixed size
            if len(all_adv_features) > 200:
                all_adv_features = all_adv_features[:200]
            else:
                all_adv_features = np.pad(all_adv_features, (0, 200 - len(all_adv_features)))
            
            advanced_features_list.append(all_adv_features)
        
        advanced_features = torch.tensor(
            np.array(advanced_features_list),
            dtype=torch.float32,
            device=x.device
        )
        
        all_features = [backbone_features, pixel_features, compression_features, advanced_features]
        fused_features, attention_weights = self.cross_attention_fusion(all_features)
        
        if self.use_meta_learning and hasattr(self, 'meta_adapter'):
            fused_features = self.meta_adapter(fused_features, support_set)
        
        uncertainty_outputs = self.uncertainty_estimator(fused_features, self.training)
        
        main_logits = self.main_classifier(fused_features)
        aux_pixel_logits = self.aux_pixel_classifier(pixel_features)
        aux_compression_logits = self.aux_compression_classifier(compression_features)
        aux_temporal_logits = self.aux_temporal_classifier(fused_features)
        
        calibrated_logits = self.calibration_layer(main_logits)
        
        outputs = {
            'logits': main_logits,
            'calibrated_logits': calibrated_logits,
            'aux_pixel_logits': aux_pixel_logits,
            'aux_compression_logits': aux_compression_logits,
            'aux_temporal_logits': aux_temporal_logits,
            'uncertainty': uncertainty_outputs['total'],
            'aleatoric_uncertainty': uncertainty_outputs['aleatoric'],
            'epistemic_uncertainty': uncertainty_outputs['epistemic'],
            'uncertainty_logits': uncertainty_outputs['logits']
        }
        
        if return_features:
            outputs['features'] = {
                'backbone': backbone_features,
                'pixel': pixel_features,
                'compression': compression_features,
                'advanced': advanced_features,
                'fused': fused_features
            }
        
        if return_attention:
            outputs['attention_weights'] = attention_weights
        
        return outputs
    
    def predict_with_confidence(self, x: torch.Tensor, 
                               temperature: float = 1.0) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Predict with temperature scaling and confidence estimation"""
        self.eval()
        
        with torch.no_grad():
            outputs = self.forward(x)
            
            # Temperature scaling for calibration
            calibrated_logits = outputs['logits'] / temperature
            probs = torch.sigmoid(calibrated_logits)
            
            # Confidence based on prediction certainty and uncertainty
            prediction_confidence = torch.abs(probs - 0.5) * 2  # Distance from decision boundary
            uncertainty_confidence = 1.0 / (outputs['uncertainty'] + 1e-8)
            
            # Combined confidence
            total_confidence = (prediction_confidence + uncertainty_confidence) / 2
            
        return probs, total_confidence, outputs['uncertainty']

class AdaptiveEnsemble(nn.Module):
    """Adaptive ensemble that weights models based on input characteristics"""
    
    def __init__(self, models: List[nn.Module], input_dim: int = 3):
        super().__init__()
        
        self.models = nn.ModuleList(models)
        self.num_models = len(models)
        
        self.weighting_network = nn.Sequential(
            nn.Conv2d(input_dim, 64, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(64, 32),
            nn.ReLU(inplace=True),
            nn.Linear(32, self.num_models),
            nn.Softmax(dim=1)
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        weights = self.weighting_network(x)
        
        # Get predictions from all models
        predictions = []
        uncertainties = []
        
        for model in self.models:
            outputs = model(x)
            predictions.append(torch.sigmoid(outputs['logits']))
            uncertainties.append(outputs['uncertainty'])
        
        # Stack predictions and uncertainties
        stacked_preds = torch.stack(predictions, dim=-1)
        stacked_uncertainties = torch.stack(uncertainties, dim=-1)
        
        ensemble_pred = torch.sum(stacked_preds * weights.unsqueeze(1), dim=-1)
        ensemble_uncertainty = torch.sum(stacked_uncertainties * weights, dim=-1)
        
        return {
            'logits': torch.logit(ensemble_pred + 1e-8),
            'predictions': ensemble_pred,
            'uncertainty': ensemble_uncertainty,
            'weights': weights,
            'individual_predictions': stacked_preds,
            'individual_uncertainties': stacked_uncertainties
        }

def create_enhanced_model(config: Dict) -> EnhancedHybridModel:
    """Factory function for enhanced model"""
    return EnhancedHybridModel(
        backbone=config.get('backbone', 'efficientnet-b4'),
        num_classes=config.get('num_classes', 1),
        pretrained=config.get('pretrained', True),
        dropout=config.get('dropout', 0.3),
        use_transformer=config.get('use_transformer', True),
        use_meta_learning=config.get('use_meta_learning', True)
    )
