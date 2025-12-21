import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class AdvancedHybridLoss(nn.Module):
    """Advanced hybrid loss function with multiple sophisticated loss components"""
    
    def __init__(self, 
                 main_weight: float = 1.0,
                 aux_pixel_weight: float = 0.3,
                 aux_compression_weight: float = 0.3,
                 uncertainty_weight: float = 0.1,
                 contrastive_weight: float = 0.2,
                 triplet_weight: float = 0.2,
                 consistency_weight: float = 0.15,
                 focal_alpha: float = 0.25,
                 focal_gamma: float = 2.0,
                 label_smoothing: float = 0.1):
        super().__init__()
        
        self.main_weight = main_weight
        self.aux_pixel_weight = aux_pixel_weight
        self.aux_compression_weight = aux_compression_weight
        self.uncertainty_weight = uncertainty_weight
        self.contrastive_weight = contrastive_weight
        self.triplet_weight = triplet_weight
        self.consistency_weight = consistency_weight
        self.focal_alpha = focal_alpha
        self.focal_gamma = focal_gamma
        self.label_smoothing = label_smoothing
        
        self.contrastive_loss = ContrastiveLoss()
        self.triplet_loss = TripletLoss()
        self.consistency_loss = ConsistencyLoss()
        self.uncertainty_aware_loss = UncertaintyAwareLoss()
        
        # Loss functions
        self.bce_loss = nn.BCEWithLogitsLoss()
        self.mse_loss = nn.MSELoss()
    
    def focal_loss(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """Enhanced focal loss with label smoothing"""
        if self.label_smoothing > 0:
            targets = targets * (1 - self.label_smoothing) + 0.5 * self.label_smoothing
        
        bce_loss = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
        pt = torch.exp(-bce_loss)
        
        alpha = torch.where(targets > 0.5, self.focal_alpha, 1 - self.focal_alpha)
        focal_loss = alpha * (1 - pt) ** self.focal_gamma * bce_loss
        return focal_loss.mean()
    
    def forward(self, outputs: dict, targets: torch.Tensor, features: torch.Tensor = None) -> dict:
        """Compute advanced hybrid loss with detailed loss breakdown"""
        losses = {}
        
        # Main classification loss with enhanced focal loss
        losses['main'] = self.focal_loss(outputs['logits'], targets)
        
        # Auxiliary losses
        losses['aux_pixel'] = self.bce_loss(outputs['aux_pixel_logits'], targets)
        losses['aux_compression'] = self.bce_loss(outputs['aux_compression_logits'], targets)
        
        if features is not None:
            losses['contrastive'] = self.contrastive_loss(features, targets)
            losses['triplet'] = self.triplet_loss(features, targets)
        else:
            losses['contrastive'] = torch.tensor(0.0, device=targets.device)
            losses['triplet'] = torch.tensor(0.0, device=targets.device)
        
        # Consistency loss for augmentation invariance
        if 'augmented_logits' in outputs:
            losses['consistency'] = self.consistency_loss(
                outputs['logits'], outputs['augmented_logits']
            )
        else:
            losses['consistency'] = torch.tensor(0.0, device=targets.device)
        
        # Enhanced uncertainty loss
        main_predictions = torch.sigmoid(outputs['logits'])
        losses['uncertainty'] = self.uncertainty_aware_loss(
            outputs['uncertainty'], main_predictions, targets
        )
        
        # Combine all losses
        total_loss = (
            self.main_weight * losses['main'] +
            self.aux_pixel_weight * losses['aux_pixel'] +
            self.aux_compression_weight * losses['aux_compression'] +
            self.uncertainty_weight * losses['uncertainty'] +
            self.contrastive_weight * losses['contrastive'] +
            self.triplet_weight * losses['triplet'] +
            self.consistency_weight * losses['consistency']
        )
        
        losses['total'] = total_loss
        return losses

class ContrastiveLoss(nn.Module):
    """Enhanced contrastive loss for learning discriminative features"""
    
    def __init__(self, margin: float = 1.0, temperature: float = 0.1):
        super().__init__()
        self.margin = margin
        self.temperature = temperature
    
    def forward(self, features: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """Compute contrastive loss with improved numerical stability"""
        batch_size = features.size(0)
        
        # Normalize features for better stability
        features = F.normalize(features, p=2, dim=1)
        
        # Compute pairwise distances
        distances = torch.cdist(features, features, p=2)
        
        # Create label matrix
        labels = labels.view(-1, 1)
        label_matrix = torch.eq(labels, labels.T).float()
        
        # Mask diagonal elements
        mask = torch.eye(batch_size, device=features.device).bool()
        distances = distances.masked_fill(mask, 0)
        label_matrix = label_matrix.masked_fill(mask, 0)
        
        # Positive pairs (same class) - minimize distance
        positive_loss = (label_matrix * distances.pow(2)).sum() / (label_matrix.sum() + 1e-8)
        
        # Negative pairs (different class) - maximize distance up to margin
        negative_distances = torch.clamp(self.margin - distances, min=0)
        negative_loss = ((1 - label_matrix) * negative_distances.pow(2)).sum() / ((1 - label_matrix).sum() + 1e-8)
        
        return positive_loss + negative_loss

class TripletLoss(nn.Module):
    """Triplet loss to ensure fake samples are farther from real samples"""
    
    def __init__(self, margin: float = 0.5, mining_strategy: str = 'hard'):
        super().__init__()
        self.margin = margin
        self.mining_strategy = mining_strategy
    
    def forward(self, features: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """Compute triplet loss with hard negative mining"""
        batch_size = features.size(0)
        
        # Normalize features
        features = F.normalize(features, p=2, dim=1)
        
        # Compute pairwise distances
        distances = torch.cdist(features, features, p=2)
        
        # Separate real and fake samples
        real_mask = (labels > 0.5).squeeze()
        fake_mask = ~real_mask
        
        if real_mask.sum() == 0 or fake_mask.sum() == 0:
            return torch.tensor(0.0, device=features.device)
        
        triplet_losses = []
        
        # For each anchor
        for i in range(batch_size):
            if real_mask[i]:  # Real anchor
                # Find hardest positive (real sample farthest from anchor)
                positive_distances = distances[i][real_mask]
                positive_distances[i] = -float('inf')  # Exclude self
                if len(positive_distances) > 1:
                    hardest_positive_dist = positive_distances.max()
                else:
                    continue
                
                # Find hardest negative (fake sample closest to anchor)
                negative_distances = distances[i][fake_mask]
                if len(negative_distances) > 0:
                    hardest_negative_dist = negative_distances.min()
                else:
                    continue
                    
            else:  # Fake anchor
                # Find hardest positive (fake sample farthest from anchor)
                positive_distances = distances[i][fake_mask]
                anchor_idx = torch.where(fake_mask)[0].tolist().index(i)
                positive_distances[anchor_idx] = -float('inf')  # Exclude self
                if len(positive_distances) > 1:
                    hardest_positive_dist = positive_distances.max()
                else:
                    continue
                
                # Find hardest negative (real sample closest to anchor)
                negative_distances = distances[i][real_mask]
                if len(negative_distances) > 0:
                    hardest_negative_dist = negative_distances.min()
                else:
                    continue
            
            # Compute triplet loss
            triplet_loss = torch.clamp(
                hardest_positive_dist - hardest_negative_dist + self.margin, 
                min=0
            )
            triplet_losses.append(triplet_loss)
        
        if triplet_losses:
            return torch.stack(triplet_losses).mean()
        else:
            return torch.tensor(0.0, device=features.device)

class ConsistencyLoss(nn.Module):
    """Consistency loss for augmentation invariance"""
    
    def __init__(self, temperature: float = 1.0):
        super().__init__()
        self.temperature = temperature
    
    def forward(self, original_logits: torch.Tensor, augmented_logits: torch.Tensor) -> torch.Tensor:
        """Compute consistency loss between original and augmented predictions"""
        # Convert logits to probabilities
        original_probs = torch.softmax(original_logits / self.temperature, dim=-1)
        augmented_probs = torch.softmax(augmented_logits / self.temperature, dim=-1)
        
        # KL divergence for consistency
        kl_loss = F.kl_div(
            torch.log(augmented_probs + 1e-8), 
            original_probs, 
            reduction='batchmean'
        )
        
        return kl_loss

class UncertaintyAwareLoss(nn.Module):
    """Enhanced uncertainty-aware loss that penalizes confident wrong predictions"""
    
    def __init__(self, confidence_penalty: float = 2.0):
        super().__init__()
        self.confidence_penalty = confidence_penalty
        self.mse_loss = nn.MSELoss()
    
    def forward(self, uncertainty: torch.Tensor, 
                predictions: torch.Tensor, 
                targets: torch.Tensor) -> torch.Tensor:
        """Compute uncertainty-aware loss with confidence penalty"""
        # Prediction error
        prediction_error = torch.abs(predictions - targets)
        
        # Confidence (inverse of uncertainty)
        confidence = 1.0 / (uncertainty + 1e-8)
        
        # Penalize high confidence wrong predictions more heavily
        confidence_penalty = confidence * prediction_error * self.confidence_penalty
        
        # Uncertainty should correlate with prediction error
        uncertainty_target = prediction_error.detach()
        uncertainty_loss = self.mse_loss(uncertainty.squeeze(), uncertainty_target.squeeze())
        
        # Combined loss
        total_loss = uncertainty_loss + confidence_penalty.mean()
        
        return total_loss

class AdaptiveFocalLoss(nn.Module):
    """Adaptive focal loss that adjusts parameters based on training progress"""
    
    def __init__(self, initial_alpha: float = 0.25, initial_gamma: float = 2.0):
        super().__init__()
        self.initial_alpha = initial_alpha
        self.initial_gamma = initial_gamma
        self.register_buffer('step_count', torch.tensor(0))
    
    def forward(self, logits: torch.Tensor, targets: torch.Tensor, epoch: int = 0) -> torch.Tensor:
        """Compute adaptive focal loss with dynamic parameters"""
        # Adapt gamma based on training progress (start high, decrease over time)
        gamma = self.initial_gamma * (0.9 ** (epoch // 10))
        gamma = max(gamma, 0.5)  # Minimum gamma
        
        # Adapt alpha based on class distribution in current batch
        positive_ratio = targets.mean()
        alpha = torch.where(targets > 0.5, positive_ratio, 1 - positive_ratio)
        
        bce_loss = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
        pt = torch.exp(-bce_loss)
        focal_loss = alpha * (1 - pt) ** gamma * bce_loss
        
        return focal_loss.mean()

class CalibrationLoss(nn.Module):
    """Calibration loss for better probability estimates"""
    
    def __init__(self, n_bins: int = 10):
        super().__init__()
        self.n_bins = n_bins
    
    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """Compute Expected Calibration Error (ECE)"""
        probs = torch.sigmoid(logits)
        
        bin_boundaries = torch.linspace(0, 1, self.n_bins + 1, device=logits.device)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        ece = torch.tensor(0.0, device=logits.device)
        
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (probs > bin_lower) & (probs <= bin_upper)
            prop_in_bin = in_bin.float().mean()
            
            if prop_in_bin > 0:
                accuracy_in_bin = targets[in_bin].mean()
                avg_confidence_in_bin = probs[in_bin].mean()
                ece += torch.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        
        return ece
