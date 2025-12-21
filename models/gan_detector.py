import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from scipy import fftpack
import cv2

class GANArtifactDetector(nn.Module):
    """
    Detects artifacts specific to GAN-generated deepfakes.
    Focuses on:
    - Spectral artifacts from GAN architectures
    - Mode collapse signatures
    - StyleGAN/ProGAN fingerprints
    - Frequency domain anomalies
    """
    
    def __init__(self, input_dim=512):
        super().__init__()
        self.input_dim = input_dim
        
        # Feature extraction layers
        self.feature_layers = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(256),
            nn.Dropout(0.3),
            
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(128),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(64)
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
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
    
    def forward(self, x):
        """Forward pass"""
        features = self.feature_layers(x)
        gan_score = self.classifier(features)
        return gan_score
    
    def extract_gan_artifacts(self, image_array):
        """
        Extract GAN-specific artifacts from image
        Returns normalized feature vector
        """
        artifacts = []
        
        # 1. Spectral analysis
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY) if len(image_array.shape) == 3 else image_array
        fft = fftpack.fft2(gray)
        magnitude = np.abs(fft)
        
        # Radial frequency analysis
        center = np.array(magnitude.shape) / 2
        y, x = np.ogrid[:magnitude.shape[0], :magnitude.shape[1]]
        r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
        
        # Analyze concentric rings
        for radius in [10, 20, 30, 40, 50]:
            mask = (r >= radius - 5) & (r < radius + 5)
            ring_energy = np.mean(magnitude[mask]) if mask.sum() > 0 else 0
            artifacts.append(ring_energy)
        
        # 2. Texture consistency
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_var = np.var(laplacian)
        artifacts.append(texture_var)
        
        # 3. Edge distribution
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges) / (gray.shape[0] * gray.shape[1])
        artifacts.append(edge_density)
        
        # 4. Color channel consistency (for RGB)
        if len(image_array.shape) == 3:
            r_chan, g_chan, b_chan = image_array[:,:,0], image_array[:,:,1], image_array[:,:,2]
            channel_diff = np.mean(np.abs(r_chan.astype(float) - g_chan.astype(float)))
            channel_diff += np.mean(np.abs(g_chan.astype(float) - b_chan.astype(float)))
            artifacts.append(channel_diff)
        
        # 5. Fourier phase distribution
        phase = np.angle(fft)
        phase_var = np.var(phase)
        artifacts.append(phase_var)
        
        # Normalize artifacts
        artifacts = np.array(artifacts, dtype=np.float32)
        artifacts = (artifacts - np.mean(artifacts)) / (np.std(artifacts) + 1e-7)
        
        # Pad to 512 dimensions
        if len(artifacts) < self.input_dim:
            artifacts = np.pad(artifacts, (0, self.input_dim - len(artifacts)), mode='constant')
        
        return artifacts[:self.input_dim]

class GANDetectorTrainer:
    """Trainer for GAN artifact detector"""
    
    def __init__(self, device='cuda'):
        self.device = device
        self.model = GANArtifactDetector().to(device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.BCELoss()
    
    def train_epoch(self, train_loader):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (features, labels) in enumerate(train_loader):
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
    detector = GANArtifactDetector()
    print(f"GAN Artifact Detector created with {sum(p.numel() for p in detector.parameters())} parameters")
    
    # Test forward pass
    dummy_input = torch.randn(4, 512)
    output = detector(dummy_input)
    print(f"Output shape: {output.shape}")
