import cv2
import numpy as np
from scipy import ndimage
from skimage.feature import local_binary_pattern, graycomatrix, graycoprops
from skimage.filters import gabor
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict, List

class PixelLevelAnalyzer:
    """Advanced pixel-level feature extraction for deepfake detection"""
    
    def __init__(self, image_size: int = 224):
        self.image_size = image_size
        self.lbp_radius = 3
        self.lbp_n_points = 8 * self.lbp_radius
        
    def extract_all_features(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract comprehensive pixel-level features"""
        features = {}
        
        # Convert to different color spaces
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # 1. Local Binary Pattern features
        features['lbp'] = self._extract_lbp_features(gray)
        
        # 2. Gradient-based features
        features['gradients'] = self._extract_gradient_features(gray)
        
        # 3. Texture features
        features['texture'] = self._extract_texture_features(gray)
        
        # 4. Color inconsistency features
        features['color'] = self._extract_color_features(image, hsv, lab)
        
        # 5. Frequency domain features
        features['frequency'] = self._extract_frequency_features(gray)
        
        # 6. Edge inconsistency features
        features['edges'] = self._extract_edge_features(gray)
        
        # 7. Pixel noise analysis
        features['noise'] = self._extract_noise_features(image)
        
        return features
    
    def _extract_lbp_features(self, gray: np.ndarray) -> np.ndarray:
        """Extract Local Binary Pattern features"""
        # Multi-scale LBP
        features = []
        
        for radius in [1, 2, 3]:
            n_points = 8 * radius
            lbp = local_binary_pattern(gray, n_points, radius, method='uniform')
            
            # LBP histogram
            hist, _ = np.histogram(lbp.ravel(), bins=n_points + 2, 
                                 range=(0, n_points + 2), density=True)
            features.extend(hist)
            
            # LBP variance (measure of local texture uniformity)
            lbp_var = ndimage.generic_filter(lbp, np.var, size=3)
            features.extend([
                np.mean(lbp_var),
                np.std(lbp_var),
                np.percentile(lbp_var, 25),
                np.percentile(lbp_var, 75)
            ])
        
        return np.array(features)
    
    def _extract_gradient_features(self, gray: np.ndarray) -> np.ndarray:
        """Extract gradient-based features for inconsistency detection"""
        # Sobel gradients
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Gradient magnitude and direction
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        direction = np.arctan2(grad_y, grad_x)
        
        # Laplacian for edge detection
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        
        features = [
            # Gradient statistics
            np.mean(magnitude), np.std(magnitude),
            np.percentile(magnitude, 25), np.percentile(magnitude, 75),
            
            # Direction consistency
            np.std(direction), np.mean(np.abs(np.diff(direction.flatten()))),
            
            # Laplacian statistics
            np.mean(np.abs(laplacian)), np.std(laplacian),
            
            # Edge density
            np.sum(magnitude > np.percentile(magnitude, 90)) / magnitude.size,
            
            # Gradient coherence (measure of local consistency)
            self._compute_gradient_coherence(grad_x, grad_y)
        ]
        
        return np.array(features)
    
    def _extract_texture_features(self, gray: np.ndarray) -> np.ndarray:
        """Extract texture-based features using GLCM and Gabor filters"""
        features = []
        
        # Gray Level Co-occurrence Matrix (GLCM)
        distances = [1, 2, 3]
        angles = [0, 45, 90, 135]
        
        for distance in distances:
            glcm = graycomatrix(gray.astype(np.uint8), [distance], 
                              [np.radians(angle) for angle in angles], 
                              levels=256, symmetric=True, normed=True)
            
            # GLCM properties
            contrast = graycoprops(glcm, 'contrast').mean()
            dissimilarity = graycoprops(glcm, 'dissimilarity').mean()
            homogeneity = graycoprops(glcm, 'homogeneity').mean()
            energy = graycoprops(glcm, 'energy').mean()
            correlation = graycoprops(glcm, 'correlation').mean()
            
            features.extend([contrast, dissimilarity, homogeneity, energy, correlation])
        
        # Gabor filter responses
        gabor_features = self._extract_gabor_features(gray)
        features.extend(gabor_features)
        
        return np.array(features)
    
    def _extract_gabor_features(self, gray: np.ndarray) -> List[float]:
        """Extract Gabor filter features"""
        features = []
        
        # Multiple orientations and frequencies
        orientations = [0, 45, 90, 135]
        frequencies = [0.1, 0.3, 0.5]
        
        for freq in frequencies:
            for orientation in orientations:
                real, _ = gabor(gray, frequency=freq, theta=np.radians(orientation))
                
                features.extend([
                    np.mean(real), np.std(real),
                    np.mean(np.abs(real)), 
                    np.percentile(np.abs(real), 90)
                ])
        
        return features
    
    def _extract_color_features(self, rgb: np.ndarray, hsv: np.ndarray, 
                               lab: np.ndarray) -> np.ndarray:
        """Extract color inconsistency features"""
        features = []
        
        # RGB channel statistics
        for channel in range(3):
            ch = rgb[:, :, channel]
            features.extend([
                np.mean(ch), np.std(ch),
                np.percentile(ch, 25), np.percentile(ch, 75)
            ])
        
        # HSV analysis
        h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
        
        # Hue consistency (circular statistics)
        hue_consistency = self._compute_hue_consistency(h)
        features.append(hue_consistency)
        
        # Saturation and value statistics
        features.extend([np.mean(s), np.std(s), np.mean(v), np.std(v)])
        
        # LAB color space analysis
        l_ch, a_ch, b_ch = lab[:, :, 0], lab[:, :, 1], lab[:, :, 2]
        features.extend([
            np.mean(l_ch), np.std(l_ch),
            np.mean(a_ch), np.std(a_ch),
            np.mean(b_ch), np.std(b_ch)
        ])
        
        # Color distribution analysis
        features.extend(self._analyze_color_distribution(rgb))
        
        return np.array(features)
    
    def _extract_frequency_features(self, gray: np.ndarray) -> np.ndarray:
        """Extract frequency domain features using FFT"""
        # 2D FFT
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude_spectrum = np.abs(fft_shift)
        
        # Log transform for better visualization
        log_spectrum = np.log(magnitude_spectrum + 1)
        
        features = [
            # Spectral statistics
            np.mean(log_spectrum), np.std(log_spectrum),
            
            # High frequency content
            self._compute_high_freq_ratio(magnitude_spectrum),
            
            # Spectral centroid
            self._compute_spectral_centroid(magnitude_spectrum),
            
            # Spectral rolloff
            self._compute_spectral_rolloff(magnitude_spectrum),
            
            # DCT features
            *self._extract_dct_features(gray)
        ]
        
        return np.array(features)
    
    def _extract_edge_features(self, gray: np.ndarray) -> np.ndarray:
        """Extract edge inconsistency features"""
        # Canny edge detection
        edges = cv2.Canny(gray.astype(np.uint8), 50, 150)
        
        # Edge density
        edge_density = np.sum(edges > 0) / edges.size
        
        # Edge continuity analysis
        edge_continuity = self._analyze_edge_continuity(edges)
        
        # Multi-scale edge analysis
        edge_features = []
        for sigma in [1, 2, 3]:
            blurred = cv2.GaussianBlur(gray, (0, 0), sigma)
            edges_scale = cv2.Canny(blurred.astype(np.uint8), 50, 150)
            edge_features.append(np.sum(edges_scale > 0) / edges_scale.size)
        
        features = [edge_density, edge_continuity] + edge_features
        return np.array(features)
    
    def _extract_noise_features(self, image: np.ndarray) -> np.ndarray:
        """Extract noise characteristics"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Estimate noise using Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # High-pass filter for noise estimation
        kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        high_pass = cv2.filter2D(gray, -1, kernel)
        noise_estimate = np.std(high_pass)
        
        # Local noise variance
        local_vars = []
        for i in range(0, gray.shape[0]-8, 8):
            for j in range(0, gray.shape[1]-8, 8):
                patch = gray[i:i+8, j:j+8]
                local_vars.append(np.var(patch))
        
        features = [
            laplacian_var,
            noise_estimate,
            np.mean(local_vars),
            np.std(local_vars),
            np.percentile(local_vars, 90)
        ]
        
        return np.array(features)
    
    # Helper methods
    def _compute_gradient_coherence(self, grad_x: np.ndarray, grad_y: np.ndarray) -> float:
        """Compute gradient coherence measure"""
        # Structure tensor
        Jxx = cv2.GaussianBlur(grad_x * grad_x, (3, 3), 1)
        Jxy = cv2.GaussianBlur(grad_x * grad_y, (3, 3), 1)
        Jyy = cv2.GaussianBlur(grad_y * grad_y, (3, 3), 1)
        
        # Eigenvalues
        trace = Jxx + Jyy
        det = Jxx * Jyy - Jxy * Jxy
        
        lambda1 = 0.5 * (trace + np.sqrt(trace**2 - 4*det + 1e-10))
        lambda2 = 0.5 * (trace - np.sqrt(trace**2 - 4*det + 1e-10))
        
        # Coherence measure
        coherence = (lambda1 - lambda2) / (lambda1 + lambda2 + 1e-10)
        return np.mean(coherence)
    
    def _compute_hue_consistency(self, hue: np.ndarray) -> float:
        """Compute hue consistency using circular statistics"""
        # Convert to radians
        hue_rad = hue * 2 * np.pi / 180
        
        # Circular mean and variance
        cos_mean = np.mean(np.cos(hue_rad))
        sin_mean = np.mean(np.sin(hue_rad))
        
        # Circular variance (1 - R where R is mean resultant length)
        R = np.sqrt(cos_mean**2 + sin_mean**2)
        circular_var = 1 - R
        
        return circular_var
    
    def _analyze_color_distribution(self, rgb: np.ndarray) -> List[float]:
        """Analyze color distribution characteristics"""
        features = []
        
        # Color histogram features
        for channel in range(3):
            hist, _ = np.histogram(rgb[:, :, channel], bins=32, range=(0, 256))
            hist = hist / np.sum(hist)  # Normalize
            
            # Histogram statistics
            features.extend([
                np.max(hist),  # Peak
                np.sum(hist**2),  # Concentration
                -np.sum(hist * np.log(hist + 1e-10))  # Entropy
            ])
        
        return features
    
    def _compute_high_freq_ratio(self, magnitude_spectrum: np.ndarray) -> float:
        """Compute ratio of high frequency content"""
        h, w = magnitude_spectrum.shape
        center_h, center_w = h // 2, w // 2
        
        # Create high frequency mask (outer region)
        y, x = np.ogrid[:h, :w]
        mask = (x - center_w)**2 + (y - center_h)**2 > (min(h, w) // 4)**2
        
        high_freq_energy = np.sum(magnitude_spectrum[mask])
        total_energy = np.sum(magnitude_spectrum)
        
        return high_freq_energy / (total_energy + 1e-10)
    
    def _compute_spectral_centroid(self, magnitude_spectrum: np.ndarray) -> float:
        """Compute spectral centroid"""
        h, w = magnitude_spectrum.shape
        y, x = np.ogrid[:h, :w]
        
        total_energy = np.sum(magnitude_spectrum)
        centroid_y = np.sum(y * magnitude_spectrum) / (total_energy + 1e-10)
        centroid_x = np.sum(x * magnitude_spectrum) / (total_energy + 1e-10)
        
        # Distance from center
        center_h, center_w = h // 2, w // 2
        centroid_dist = np.sqrt((centroid_x - center_w)**2 + (centroid_y - center_h)**2)
        
        return centroid_dist / max(h, w)
    
    def _compute_spectral_rolloff(self, magnitude_spectrum: np.ndarray, rolloff=0.85) -> float:
        """Compute spectral rolloff"""
        # Flatten and sort spectrum
        spectrum_flat = magnitude_spectrum.flatten()
        spectrum_sorted = np.sort(spectrum_flat)[::-1]
        
        # Find rolloff point
        cumsum = np.cumsum(spectrum_sorted)
        total_energy = cumsum[-1]
        rolloff_idx = np.where(cumsum >= rolloff * total_energy)[0][0]
        
        return rolloff_idx / len(spectrum_flat)
    
    def _extract_dct_features(self, gray: np.ndarray) -> List[float]:
        """Extract DCT-based features"""
        # 2D DCT
        dct = cv2.dct(gray.astype(np.float32))
        
        # Extract low-frequency coefficients
        dct_low = dct[:8, :8]
        
        features = [
            np.mean(np.abs(dct_low)),
            np.std(dct_low),
            np.sum(np.abs(dct_low[1:, 1:]))  # AC coefficients
        ]
        
        return features
    
    def _analyze_edge_continuity(self, edges: np.ndarray) -> float:
        """Analyze edge continuity"""
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 0.0
        
        # Analyze contour properties
        total_length = sum(cv2.arcLength(contour, False) for contour in contours)
        avg_length = total_length / len(contours) if contours else 0
        
        # Continuity measure based on average contour length
        return avg_length / max(edges.shape)

class PixelFeatureExtractor(nn.Module):
    """Neural network module for pixel-level feature extraction"""
    
    def __init__(self, input_channels: int = 3, feature_dim: int = 512):
        super().__init__()
        
        self.pixel_analyzer = PixelLevelAnalyzer()
        
        # Convolutional layers for learning pixel patterns
        self.conv_layers = nn.Sequential(
            nn.Conv2d(input_channels, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            nn.Conv2d(128, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        
        # Feature fusion layer
        self.feature_fusion = nn.Sequential(
            nn.Linear(256 + 200, feature_dim),  # 200 is approx handcrafted features
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(feature_dim, feature_dim)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.size(0)
        
        # CNN features
        cnn_features = self.conv_layers(x)
        cnn_features = cnn_features.view(batch_size, -1)
        
        # Handcrafted pixel features (computed on CPU)
        handcrafted_features = []
        for i in range(batch_size):
            img_np = x[i].permute(1, 2, 0).cpu().numpy()
            img_np = (img_np * 255).astype(np.uint8)
            
            features = self.pixel_analyzer.extract_all_features(img_np)
            # Concatenate all feature types
            all_features = np.concatenate([
                features['lbp'][:50],  # Truncate to manageable size
                features['gradients'],
                features['texture'][:30],
                features['color'],
                features['frequency'],
                features['edges'],
                features['noise']
            ])
            
            # Pad or truncate to fixed size
            if len(all_features) > 200:
                all_features = all_features[:200]
            else:
                all_features = np.pad(all_features, (0, 200 - len(all_features)))
            
            handcrafted_features.append(all_features)
        
        handcrafted_features = torch.tensor(
            np.array(handcrafted_features), 
            dtype=torch.float32, 
            device=x.device
        )
        
        # Combine features
        combined_features = torch.cat([cnn_features, handcrafted_features], dim=1)
        output = self.feature_fusion(combined_features)
        
        return output
