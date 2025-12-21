import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from scipy import signal

class DiffusionForensicsExtractor(nn.Module):
    """
    Detects artifacts specific to Diffusion model-generated deepfakes.
    Focuses on:
    - Diffusion step artifacts
    - Reverse process signatures
    - Temporal inconsistencies
    - Latent space manipulation patterns
    """
    
    def __init__(self, input_dim=512):
        super().__init__()
        self.input_dim = input_dim
        
        # 3D convolution for temporal patterns
        self.temporal_layers = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(16),
            
            nn.Conv1d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(32),
            
            nn.AdaptiveAvgPool1d(1)
        )
        
        # Feature processing
        self.feature_layers = nn.Sequential(
            nn.Linear(32 + 480, 256),  # 32 from temporal + 480 from input features
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(256),
            nn.Dropout(0.3),
            
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(128),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.ReLU(inplace=True)
        )
        
        # Output layer
        self.classifier = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(inplace=True),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights"""
        for module in self.modules():
            if isinstance(module, (nn.Linear, nn.Conv1d)):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
    
    def forward(self, x, temporal_features=None):
        """Forward pass"""
        if temporal_features is not None:
            temporal_features = temporal_features.unsqueeze(1)  # Add channel dim
            temporal_out = self.temporal_layers(temporal_features)
            temporal_out = temporal_out.view(temporal_out.size(0), -1)
            x = torch.cat([temporal_out, x[:, 32:]], dim=1)  # Concatenate temporal features
        
        features = self.feature_layers(x)
        diffusion_score = self.classifier(features)
        return diffusion_score
    
    def extract_diffusion_artifacts(self, image_array):
        """
        Extract Diffusion-specific artifacts from image
        Returns normalized feature vector
        """
        artifacts = []
        
        # 1. Noise distribution analysis
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY) if len(image_array.shape) == 3 else image_array
        gray_float = gray.astype(np.float32) / 255.0
        
        # Apply Laplacian (derivative) to detect noise
        laplacian = cv2.Laplacian(gray_float, cv2.CV_64F)
        noise_mean = np.mean(np.abs(laplacian))
        noise_std = np.std(laplacian)
        artifacts.extend([noise_mean, noise_std])
        
        # 2. Wavelet decomposition (Haar wavelet)
        # 4-level decomposition
        current = gray_float
        for level in range(4):
            # Simple Haar-like decomposition
            h, w = current.shape
            h_half, w_half = h // 2, w // 2
            
            ll = current[:h_half, :w_half]  # Low-low
            lh = current[:h_half, w_half:]   # Low-high
            hl = current[h_half:, :w_half]   # High-low
            hh = current[h_half:, w_half:]   # High-high
            
            # Energy in detail coefficients
            detail_energy = np.mean(np.abs(lh)) + np.mean(np.abs(hl)) + np.mean(np.abs(hh))
            artifacts.append(detail_energy)
            
            current = ll
        
        # 3. Gradient consistency
        gx = cv2.Sobel(gray_float, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray_float, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(gx**2 + gy**2)
        
        # Gradient entropy
        hist, _ = np.histogram(gradient_magnitude.flatten(), bins=256, range=(0, np.max(gradient_magnitude)))
        hist = hist / np.sum(hist)
        grad_entropy = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0]))
        artifacts.append(grad_entropy)
        
        # 4. Diffusion timestep indicators
        # Smooth regions (less diffusion) vs structured regions
        blur = cv2.GaussianBlur(gray, (5, 5), 1.0)
        diff_from_blur = np.mean(np.abs(gray_float - blur.astype(np.float32) / 255.0))
        artifacts.append(diff_from_blur)
        
        # 5. Color consistency in diffusion process
        if len(image_array.shape) == 3:
            for i in range(3):
                channel_laplacian = cv2.Laplacian(image_array[:,:,i].astype(np.float32), cv2.CV_64F)
                artifacts.append(np.std(channel_laplacian))
        
        # 6. Frequency domain analysis (diffusion typically smooths high frequencies)
        fft = np.fft.fft2(gray_float)
        magnitude = np.abs(fft)
        
        # High frequency content
        h, w = magnitude.shape
        center_h, center_w = h // 2, w // 2
        high_freq_region = magnitude[center_h-20:center_h+20, center_w-20:center_w+20]
        high_freq_energy = np.mean(high_freq_region)
        artifacts.append(high_freq_energy)
        
        # Normalize artifacts
        artifacts = np.array(artifacts, dtype=np.float32)
        artifacts = (artifacts - np.mean(artifacts)) / (np.std(artifacts) + 1e-7)
        
        # Pad to 512 dimensions
        if len(artifacts) < self.input_dim:
            artifacts = np.pad(artifacts, (0, self.input_dim - len(artifacts)), mode='constant')
        
        return artifacts[:self.input_dim]

class DiffusionDetectorTrainer:
    """Trainer for Diffusion forensics detector"""
    
    def __init__(self, device='cuda'):
        self.device = device
        self.model = DiffusionForensicsExtractor().to(device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.BCELoss()
    
    def train_epoch(self, train_loader):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for features, labels in train_loader:
            features = features.to(self.device)
            labels = labels.to(self.device).unsqueeze(1).float()
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(features)
            loss = self.criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            total_loss += loss.item()
            predictions = (outputs > 0.5).float()
            correct += (predictions == labels).sum().item()
            total += labels.size(0)
        
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
            for features, labels in val_loader:
                features = features.to(self.device)
                labels = labels.to(self.device).unsqueeze(1).float()
                
                outputs = self.model(features)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                predictions = (outputs > 0.5).float()
                correct += (predictions == labels).sum().item()
                total += labels.size(0)
        
        avg_loss = total_loss / len(val_loader)
        accuracy = 100 * correct / total
        
        return avg_loss, accuracy

if __name__ == "__main__":
    detector = DiffusionForensicsExtractor()
    print(f"Diffusion Forensics Extractor created with {sum(p.numel() for p in detector.parameters())} parameters")
    
    # Test forward pass
    dummy_input = torch.randn(4, 512)
    output = detector(dummy_input)
    print(f"Output shape: {output.shape}")
