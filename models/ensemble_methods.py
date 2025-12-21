import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from scipy import stats
import math

class BayesianLinear(nn.Module):
    """Bayesian linear layer with weight uncertainty"""
    
    def __init__(self, in_features: int, out_features: int, prior_std: float = 1.0):
        super().__init__()
        
        self.in_features = in_features
        self.out_features = out_features
        self.prior_std = prior_std
        
        # Weight parameters (mean and log variance)
        self.weight_mu = nn.Parameter(torch.randn(out_features, in_features) * 0.1)
        self.weight_logvar = nn.Parameter(torch.randn(out_features, in_features) * 0.1 - 5)
        
        # Bias parameters
        self.bias_mu = nn.Parameter(torch.randn(out_features) * 0.1)
        self.bias_logvar = nn.Parameter(torch.randn(out_features) * 0.1 - 5)
        
        # Prior parameters
        self.register_buffer('prior_weight_mu', torch.zeros(out_features, in_features))
        self.register_buffer('prior_weight_std', torch.ones(out_features, in_features) * prior_std)
        self.register_buffer('prior_bias_mu', torch.zeros(out_features))
        self.register_buffer('prior_bias_std', torch.ones(out_features) * prior_std)
    
    def forward(self, x: torch.Tensor, sample: bool = True) -> torch.Tensor:
        if sample:
            # Sample weights and biases
            weight_std = torch.exp(0.5 * self.weight_logvar)
            weight = self.weight_mu + weight_std * torch.randn_like(weight_std)
            
            bias_std = torch.exp(0.5 * self.bias_logvar)
            bias = self.bias_mu + bias_std * torch.randn_like(bias_std)
        else:
            # Use mean values
            weight = self.weight_mu
            bias = self.bias_mu
        
        return F.linear(x, weight, bias)
    
    def kl_divergence(self) -> torch.Tensor:
        """Compute KL divergence between posterior and prior"""
        # Weight KL divergence
        weight_var = torch.exp(self.weight_logvar)
        weight_kl = 0.5 * torch.sum(
            (self.weight_mu - self.prior_weight_mu)**2 / self.prior_weight_std**2 +
            weight_var / self.prior_weight_std**2 -
            1 - self.weight_logvar + 2 * torch.log(self.prior_weight_std)
        )
        
        # Bias KL divergence
        bias_var = torch.exp(self.bias_logvar)
        bias_kl = 0.5 * torch.sum(
            (self.bias_mu - self.prior_bias_mu)**2 / self.prior_bias_std**2 +
            bias_var / self.prior_bias_std**2 -
            1 - self.bias_logvar + 2 * torch.log(self.prior_bias_std)
        )
        
        return weight_kl + bias_kl

class BayesianDeepfakeDetector(nn.Module):
    """Bayesian neural network for uncertainty quantification"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int], num_classes: int = 1):
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.num_classes = num_classes
        
        # Build Bayesian layers
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.append(BayesianLinear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            prev_dim = hidden_dim
        
        layers.append(BayesianLinear(prev_dim, num_classes))
        
        self.layers = nn.ModuleList([layer for layer in layers if isinstance(layer, BayesianLinear)])
        self.activations = nn.ModuleList([layer for layer in layers if not isinstance(layer, BayesianLinear)])
    
    def forward(self, x: torch.Tensor, num_samples: int = 1) -> Dict[str, torch.Tensor]:
        if num_samples == 1:
            # Single forward pass
            output = x
            layer_idx = 0
            activation_idx = 0
            
            for i in range(len(self.layers) + len(self.activations)):
                if i % 2 == 0 and layer_idx < len(self.layers):
                    output = self.layers[layer_idx](output, sample=self.training)
                    layer_idx += 1
                elif activation_idx < len(self.activations):
                    output = self.activations[activation_idx](output)
                    activation_idx += 1
            
            return {'logits': output, 'uncertainty': torch.zeros_like(output)}
        
        else:
            # Multiple samples for uncertainty estimation
            samples = []
            for _ in range(num_samples):
                output = x
                layer_idx = 0
                activation_idx = 0
                
                for i in range(len(self.layers) + len(self.activations)):
                    if i % 2 == 0 and layer_idx < len(self.layers):
                        output = self.layers[layer_idx](output, sample=True)
                        layer_idx += 1
                    elif activation_idx < len(self.activations):
                        output = self.activations[activation_idx](output)
                        activation_idx += 1
                
                samples.append(output)
            
            samples = torch.stack(samples, dim=0)
            mean_logits = torch.mean(samples, dim=0)
            uncertainty = torch.var(samples, dim=0)
            
            return {'logits': mean_logits, 'uncertainty': uncertainty, 'samples': samples}
    
    def kl_loss(self) -> torch.Tensor:
        """Compute total KL divergence loss"""
        kl_loss = 0
        for layer in self.layers:
            kl_loss += layer.kl_divergence()
        return kl_loss

class TestTimeAugmentation:
    """Test-time augmentation for improved predictions"""
    
    def __init__(self, augmentations: List[Callable], num_augmentations: int = 8):
        self.augmentations = augmentations
        self.num_augmentations = num_augmentations
    
    def __call__(self, model: nn.Module, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        model.eval()
        predictions = []
        uncertainties = []
        
        with torch.no_grad():
            # Original prediction
            outputs = model(x)
            predictions.append(torch.sigmoid(outputs['logits']))
            if 'uncertainty' in outputs:
                uncertainties.append(outputs['uncertainty'])
            
            # Augmented predictions
            for _ in range(self.num_augmentations - 1):
                # Apply random augmentation
                aug_func = np.random.choice(self.augmentations)
                x_aug = aug_func(x)
                
                outputs_aug = model(x_aug)
                predictions.append(torch.sigmoid(outputs_aug['logits']))
                if 'uncertainty' in outputs_aug:
                    uncertainties.append(outputs_aug['uncertainty'])
        
        # Aggregate predictions
        stacked_preds = torch.stack(predictions, dim=0)
        mean_pred = torch.mean(stacked_preds, dim=0)
        pred_uncertainty = torch.var(stacked_preds, dim=0)
        
        result = {
            'predictions': mean_pred,
            'logits': torch.logit(mean_pred + 1e-8),
            'prediction_uncertainty': pred_uncertainty
        }
        
        if uncertainties:
            stacked_uncertainties = torch.stack(uncertainties, dim=0)
            result['model_uncertainty'] = torch.mean(stacked_uncertainties, dim=0)
            result['total_uncertainty'] = pred_uncertainty + result['model_uncertainty']
        
        return result

class DeepEnsemble(nn.Module):
    """Deep ensemble with multiple independently trained models"""
    
    def __init__(self, models: List[nn.Module], ensemble_method: str = 'average'):
        super().__init__()
        
        self.models = nn.ModuleList(models)
        self.ensemble_method = ensemble_method
        self.num_models = len(models)
        
        if ensemble_method == 'learned':
            # Meta-learner for ensemble weights
            self.meta_learner = nn.Sequential(
                nn.Linear(self.num_models, 64),
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, self.num_models),
                nn.Softmax(dim=1)
            )
    
    def forward(self, x: torch.Tensor, return_individual: bool = False) -> Dict[str, torch.Tensor]:
        predictions = []
        uncertainties = []
        individual_outputs = []
        
        for model in self.models:
            outputs = model(x)
            pred = torch.sigmoid(outputs['logits'])
            predictions.append(pred)
            individual_outputs.append(outputs)
            
            if 'uncertainty' in outputs:
                uncertainties.append(outputs['uncertainty'])
        
        stacked_preds = torch.stack(predictions, dim=0)
        
        if self.ensemble_method == 'average':
            ensemble_pred = torch.mean(stacked_preds, dim=0)
            
        elif self.ensemble_method == 'weighted':
            # Inverse uncertainty weighting
            if uncertainties:
                stacked_uncertainties = torch.stack(uncertainties, dim=0)
                weights = 1.0 / (stacked_uncertainties + 1e-8)
                weights = weights / torch.sum(weights, dim=0, keepdim=True)
                ensemble_pred = torch.sum(stacked_preds * weights, dim=0)
            else:
                ensemble_pred = torch.mean(stacked_preds, dim=0)
                
        elif self.ensemble_method == 'learned':
            # Use meta-learner to determine weights
            pred_features = stacked_preds.permute(1, 2, 0).squeeze()  # [batch, num_models]
            weights = self.meta_learner(pred_features)
            ensemble_pred = torch.sum(stacked_preds * weights.unsqueeze(1).permute(2, 0, 1), dim=0)
        
        # Ensemble uncertainty (disagreement + average individual uncertainty)
        ensemble_disagreement = torch.var(stacked_preds, dim=0)
        
        if uncertainties:
            stacked_uncertainties = torch.stack(uncertainties, dim=0)
            avg_individual_uncertainty = torch.mean(stacked_uncertainties, dim=0)
            total_uncertainty = ensemble_disagreement + avg_individual_uncertainty
        else:
            total_uncertainty = ensemble_disagreement
        
        result = {
            'predictions': ensemble_pred,
            'logits': torch.logit(ensemble_pred + 1e-8),
            'uncertainty': total_uncertainty,
            'disagreement': ensemble_disagreement
        }
        
        if return_individual:
            result['individual_predictions'] = stacked_preds
            result['individual_outputs'] = individual_outputs
        
        return result

class CalibrationModule(nn.Module):
    """Temperature scaling and Platt scaling for probability calibration"""
    
    def __init__(self, method: str = 'temperature'):
        super().__init__()
        
        self.method = method
        
        if method == 'temperature':
            self.temperature = nn.Parameter(torch.ones(1))
        elif method == 'platt':
            self.platt_a = nn.Parameter(torch.ones(1))
            self.platt_b = nn.Parameter(torch.zeros(1))
    
    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        if self.method == 'temperature':
            return torch.sigmoid(logits / self.temperature)
        elif self.method == 'platt':
            return torch.sigmoid(self.platt_a * logits + self.platt_b)
        else:
            return torch.sigmoid(logits)
    
    def fit_calibration(self, logits: torch.Tensor, targets: torch.Tensor, 
                       max_iter: int = 100, lr: float = 0.01):
        """Fit calibration parameters on validation set"""
        optimizer = torch.optim.LBFGS([p for p in self.parameters()], lr=lr, max_iter=max_iter)
        
        def closure():
            optimizer.zero_grad()
            calibrated_probs = self.forward(logits)
            loss = F.binary_cross_entropy(calibrated_probs, targets)
            loss.backward()
            return loss
        
        optimizer.step(closure)

class StackingEnsemble(nn.Module):
    """Stacking ensemble with meta-learner"""
    
    def __init__(self, base_models: List[nn.Module], meta_learner: nn.Module):
        super().__init__()
        
        self.base_models = nn.ModuleList(base_models)
        self.meta_learner = meta_learner
        self.num_models = len(base_models)
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        # Get predictions from base models
        base_predictions = []
        base_uncertainties = []
        
        for model in self.base_models:
            outputs = model(x)
            pred = torch.sigmoid(outputs['logits'])
            base_predictions.append(pred)
            
            if 'uncertainty' in outputs:
                base_uncertainties.append(outputs['uncertainty'])
        
        # Stack base predictions as features for meta-learner
        stacked_preds = torch.cat(base_predictions, dim=1)  # [batch, num_models]
        
        # Meta-learner prediction
        meta_outputs = self.meta_learner(stacked_preds)
        final_pred = torch.sigmoid(meta_outputs['logits'])
        
        # Combine uncertainties
        if base_uncertainties:
            stacked_uncertainties = torch.stack(base_uncertainties, dim=0)
            base_uncertainty = torch.mean(stacked_uncertainties, dim=0)
            
            if 'uncertainty' in meta_outputs:
                total_uncertainty = base_uncertainty + meta_outputs['uncertainty']
            else:
                total_uncertainty = base_uncertainty
        else:
            total_uncertainty = meta_outputs.get('uncertainty', torch.zeros_like(final_pred))
        
        return {
            'predictions': final_pred,
            'logits': meta_outputs['logits'],
            'uncertainty': total_uncertainty,
            'base_predictions': torch.stack(base_predictions, dim=0)
        }

class UncertaintyAwareEnsemble(nn.Module):
    """Ensemble that adapts based on prediction uncertainty"""
    
    def __init__(self, models: List[nn.Module], uncertainty_threshold: float = 0.1):
        super().__init__()
        
        self.models = nn.ModuleList(models)
        self.uncertainty_threshold = uncertainty_threshold
        self.num_models = len(models)
        
        # Uncertainty-based weighting network
        self.uncertainty_weighter = nn.Sequential(
            nn.Linear(self.num_models, 32),
            nn.ReLU(),
            nn.Linear(32, self.num_models),
            nn.Softmax(dim=1)
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        predictions = []
        uncertainties = []
        
        for model in self.models:
            outputs = model(x)
            pred = torch.sigmoid(outputs['logits'])
            predictions.append(pred)
            
            if 'uncertainty' in outputs:
                uncertainties.append(outputs['uncertainty'])
            else:
                # Estimate uncertainty from prediction confidence
                confidence = torch.abs(pred - 0.5) * 2
                uncertainty = 1.0 - confidence
                uncertainties.append(uncertainty)
        
        stacked_preds = torch.stack(predictions, dim=0)
        stacked_uncertainties = torch.stack(uncertainties, dim=0)
        
        # Adaptive weighting based on uncertainties
        uncertainty_features = stacked_uncertainties.permute(1, 2, 0).squeeze()
        weights = self.uncertainty_weighter(uncertainty_features)
        
        # Apply weights
        weighted_preds = torch.sum(stacked_preds * weights.unsqueeze(1).permute(2, 0, 1), dim=0)
        
        # High uncertainty regions use more models
        high_uncertainty_mask = torch.mean(stacked_uncertainties, dim=0) > self.uncertainty_threshold
        
        # For high uncertainty regions, use equal weighting
        equal_weight_pred = torch.mean(stacked_preds, dim=0)
        final_pred = torch.where(high_uncertainty_mask, equal_weight_pred, weighted_preds)
        
        # Final uncertainty estimation
        disagreement = torch.var(stacked_preds, dim=0)
        avg_uncertainty = torch.mean(stacked_uncertainties, dim=0)
        total_uncertainty = disagreement + avg_uncertainty
        
        return {
            'predictions': final_pred,
            'logits': torch.logit(final_pred + 1e-8),
            'uncertainty': total_uncertainty,
            'disagreement': disagreement,
            'weights': weights,
            'high_uncertainty_mask': high_uncertainty_mask
        }

def create_augmentation_functions():
    """Create list of augmentation functions for TTA"""
    
    def horizontal_flip(x):
        return torch.flip(x, dims=[3])
    
    def vertical_flip(x):
        return torch.flip(x, dims=[2])
    
    def rotate_90(x):
        return torch.rot90(x, k=1, dims=[2, 3])
    
    def rotate_180(x):
        return torch.rot90(x, k=2, dims=[2, 3])
    
    def rotate_270(x):
        return torch.rot90(x, k=3, dims=[2, 3])
    
    def add_noise(x, noise_level=0.01):
        noise = torch.randn_like(x) * noise_level
        return torch.clamp(x + noise, 0, 1)
    
    def brightness_adjust(x, factor=0.1):
        adjustment = torch.randn(x.size(0), 1, 1, 1, device=x.device) * factor
        return torch.clamp(x + adjustment, 0, 1)
    
    def contrast_adjust(x, factor=0.1):
        mean_val = torch.mean(x, dim=[2, 3], keepdim=True)
        adjustment = 1 + torch.randn(x.size(0), 1, 1, 1, device=x.device) * factor
        return torch.clamp((x - mean_val) * adjustment + mean_val, 0, 1)
    
    return [
        horizontal_flip, vertical_flip, rotate_90, rotate_180, rotate_270,
        add_noise, brightness_adjust, contrast_adjust
    ]

class EnsembleManager:
    """Manager class for different ensemble methods"""
    
    def __init__(self):
        self.ensemble_methods = {
            'deep_ensemble': DeepEnsemble,
            'stacking': StackingEnsemble,
            'uncertainty_aware': UncertaintyAwareEnsemble,
            'bayesian': BayesianDeepfakeDetector
        }
        
        self.augmentation_functions = create_augmentation_functions()
        self.tta = TestTimeAugmentation(self.augmentation_functions)
    
    def create_ensemble(self, method: str, models: List[nn.Module], **kwargs):
        """Create ensemble of specified type"""
        if method not in self.ensemble_methods:
            raise ValueError(f"Unknown ensemble method: {method}")
        
        if method == 'stacking':
            meta_learner = kwargs.get('meta_learner')
            if meta_learner is None:
                raise ValueError("Meta-learner required for stacking ensemble")
            return StackingEnsemble(models, meta_learner)
        else:
            return self.ensemble_methods[method](models, **kwargs)
    
    def apply_tta(self, model: nn.Module, x: torch.Tensor, num_augmentations: int = 8):
        """Apply test-time augmentation"""
        self.tta.num_augmentations = num_augmentations
        return self.tta(model, x)
    
    def calibrate_model(self, model: nn.Module, val_logits: torch.Tensor, 
                       val_targets: torch.Tensor, method: str = 'temperature'):
        """Calibrate model probabilities"""
        calibration_module = CalibrationModule(method)
        calibration_module.fit_calibration(val_logits, val_targets)
        return calibration_module
