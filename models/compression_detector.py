import cv2
import numpy as np
from scipy import ndimage, fftpack
from scipy.signal import convolve2d
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class CompressionArtifactDetector:
    """Advanced compression artifact detection for deepfake analysis"""
    
    def __init__(self):
        # JPEG quantization tables (standard)
        self.jpeg_qtable_luma = np.array([
            [16, 11, 10, 16, 24, 40, 51, 61],
            [12, 12, 14, 19, 26, 58, 60, 55],
            [14, 13, 16, 24, 40, 57, 69, 56],
            [14, 17, 22, 29, 51, 87, 80, 62],
            [18, 22, 37, 56, 68, 109, 103, 77],
            [24, 35, 55, 64, 81, 104, 113, 92],
            [49, 64, 78, 87, 103, 121, 120, 101],
            [72, 92, 95, 98, 112, 100, 103, 99]
        ])
        
        # Blocking artifact detection kernels
        self.blocking_kernels = self._create_blocking_kernels()
        
    def detect_all_artifacts(self, image: np.ndarray) -> Dict[str, float]:
        """Detect all types of compression artifacts"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
            
        artifacts = {}
        
        # 1. JPEG blocking artifacts
        artifacts.update(self._detect_blocking_artifacts(gray))
        
        # 2. Quantization noise
        artifacts.update(self._detect_quantization_noise(gray))
        
        # 3. Double compression detection
        artifacts.update(self._detect_double_compression(gray))
        
        # 4. Compression inconsistency
        artifacts.update(self._detect_compression_inconsistency(image))
        
        # 5. DCT coefficient analysis
        artifacts.update(self._analyze_dct_coefficients(gray))
        
        # 6. Frequency domain artifacts
        artifacts.update(self._detect_frequency_artifacts(gray))
        
        # 7. Ringing artifacts
        artifacts.update(self._detect_ringing_artifacts(gray))
        
        return artifacts
    
    def _detect_blocking_artifacts(self, gray: np.ndarray) -> Dict[str, float]:
        """Detect JPEG blocking artifacts"""
        features = {}
        
        # Horizontal and vertical blocking
        h_blocking = self._measure_blocking_direction(gray, 'horizontal')
        v_blocking = self._measure_blocking_direction(gray, 'vertical')
        
        features['h_blocking'] = h_blocking
        features['v_blocking'] = v_blocking
        features['avg_blocking'] = (h_blocking + v_blocking) / 2
        
        # Grid-based blocking detection
        grid_blocking = self._detect_grid_blocking(gray)
        features['grid_blocking'] = grid_blocking
        
        # Blocking artifact strength using specialized kernels
        blocking_strength = self._compute_blocking_strength(gray)
        features['blocking_strength'] = blocking_strength
        
        return features
    
    def _measure_blocking_direction(self, gray: np.ndarray, direction: str) -> float:
        """Measure blocking artifacts in specific direction"""
        if direction == 'horizontal':
            # Detect horizontal block boundaries
            diff = np.abs(np.diff(gray, axis=0))
            # Look for periodic patterns every 8 pixels (JPEG block size)
            blocking_score = 0
            for i in range(7, gray.shape[0]-1, 8):
                if i < diff.shape[0]:
                    blocking_score += np.mean(diff[i, :])
        else:  # vertical
            diff = np.abs(np.diff(gray, axis=1))
            blocking_score = 0
            for j in range(7, gray.shape[1]-1, 8):
                if j < diff.shape[1]:
                    blocking_score += np.mean(diff[:, j])
        
        return blocking_score / max(gray.shape)
    
    def _detect_grid_blocking(self, gray: np.ndarray) -> float:
        """Detect 8x8 grid blocking pattern"""
        h, w = gray.shape
        blocking_score = 0
        count = 0
        
        # Check 8x8 block boundaries
        for i in range(8, h-8, 8):
            for j in range(8, w-8, 8):
                # Measure discontinuity at block boundaries
                # Horizontal boundary
                top_edge = gray[i-1, j:j+8]
                bottom_edge = gray[i, j:j+8]
                h_discontinuity = np.mean(np.abs(top_edge - bottom_edge))
                
                # Vertical boundary
                left_edge = gray[i:i+8, j-1]
                right_edge = gray[i:i+8, j]
                v_discontinuity = np.mean(np.abs(left_edge - right_edge))
                
                blocking_score += (h_discontinuity + v_discontinuity)
                count += 1
        
        return blocking_score / (count + 1e-10)
    
    def _compute_blocking_strength(self, gray: np.ndarray) -> float:
        """Compute blocking artifact strength using convolution"""
        blocking_scores = []
        
        for kernel in self.blocking_kernels:
            response = np.abs(convolve2d(gray, kernel, mode='valid'))
            blocking_scores.append(np.mean(response))
        
        return np.mean(blocking_scores)
    
    def _detect_quantization_noise(self, gray: np.ndarray) -> Dict[str, float]:
        """Detect quantization noise patterns"""
        features = {}
        
        # DCT-based quantization noise detection
        dct_noise = self._analyze_dct_quantization(gray)
        features['dct_quantization'] = dct_noise
        
        # Histogram-based quantization detection
        hist_quantization = self._detect_histogram_quantization(gray)
        features['hist_quantization'] = hist_quantization
        
        # Local variance analysis
        local_var_pattern = self._analyze_local_variance_pattern(gray)
        features['local_var_pattern'] = local_var_pattern
        
        return features
    
    def _analyze_dct_quantization(self, gray: np.ndarray) -> float:
        """Analyze DCT coefficients for quantization patterns"""
        h, w = gray.shape
        quantization_score = 0
        count = 0
        
        # Process 8x8 blocks
        for i in range(0, h-8, 8):
            for j in range(0, w-8, 8):
                block = gray[i:i+8, j:j+8].astype(np.float32)
                
                # DCT transform
                dct_block = cv2.dct(block)
                
                # Analyze coefficient distribution
                # Quantized coefficients tend to cluster around multiples of quantization steps
                for u in range(8):
                    for v in range(8):
                        if u > 0 or v > 0:  # Skip DC coefficient
                            coeff = dct_block[u, v]
                            # Check if coefficient is close to quantization levels
                            q_step = self.jpeg_qtable_luma[u, v]
                            quantized = np.round(coeff / q_step) * q_step
                            quantization_error = abs(coeff - quantized)
                            quantization_score += quantization_error
                            count += 1
        
        return quantization_score / (count + 1e-10)
    
    def _detect_histogram_quantization(self, gray: np.ndarray) -> float:
        """Detect quantization through histogram analysis"""
        hist, bins = np.histogram(gray, bins=256, range=(0, 256))
        
        # Look for periodic peaks in histogram (sign of quantization)
        # Smooth histogram to reduce noise
        smoothed_hist = ndimage.gaussian_filter1d(hist.astype(float), sigma=1)
        
        # Find peaks
        peaks = []
        for i in range(1, len(smoothed_hist)-1):
            if (smoothed_hist[i] > smoothed_hist[i-1] and 
                smoothed_hist[i] > smoothed_hist[i+1] and
                smoothed_hist[i] > np.mean(smoothed_hist)):
                peaks.append(i)
        
        # Analyze peak spacing (quantized images have regular peak spacing)
        if len(peaks) > 2:
            spacings = np.diff(peaks)
            spacing_regularity = 1.0 / (np.std(spacings) + 1e-10)
        else:
            spacing_regularity = 0
        
        return min(spacing_regularity, 10.0)  # Cap the value
    
    def _analyze_local_variance_pattern(self, gray: np.ndarray) -> float:
        """Analyze local variance patterns indicative of quantization"""
        # Compute local variance in 4x4 windows
        h, w = gray.shape
        variances = []
        
        for i in range(0, h-4, 2):
            for j in range(0, w-4, 2):
                patch = gray[i:i+4, j:j+4]
                variances.append(np.var(patch))
        
        variances = np.array(variances)
        
        # Quantized images have characteristic variance distribution
        # Low variance regions (flat areas) and high variance regions (edges)
        var_hist, _ = np.histogram(variances, bins=50)
        var_hist = var_hist / np.sum(var_hist)
        
        # Measure bimodality (two peaks: low and high variance)
        bimodality = self._measure_bimodality(var_hist)
        
        return bimodality
    
    def _detect_double_compression(self, gray: np.ndarray) -> Dict[str, float]:
        """Detect double JPEG compression"""
        features = {}
        
        # DCT coefficient histogram analysis
        dct_double_comp = self._analyze_dct_double_compression(gray)
        features['dct_double_compression'] = dct_double_comp
        
        # Benford's law analysis on DCT coefficients
        benford_score = self._benford_law_analysis(gray)
        features['benford_violation'] = benford_score
        
        # Blocking artifact inconsistency
        blocking_inconsistency = self._detect_blocking_inconsistency(gray)
        features['blocking_inconsistency'] = blocking_inconsistency
        
        return features
    
    def _analyze_dct_double_compression(self, gray: np.ndarray) -> float:
        """Analyze DCT coefficients for double compression signatures"""
        h, w = gray.shape
        all_coeffs = []
        
        # Extract all AC coefficients
        for i in range(0, h-8, 8):
            for j in range(0, w-8, 8):
                block = gray[i:i+8, j:j+8].astype(np.float32)
                dct_block = cv2.dct(block)
                
                # Collect AC coefficients
                for u in range(8):
                    for v in range(8):
                        if u > 0 or v > 0:  # Skip DC
                            all_coeffs.append(dct_block[u, v])
        
        all_coeffs = np.array(all_coeffs)
        
        # Analyze coefficient distribution
        # Double compression creates characteristic patterns
        hist, bins = np.histogram(all_coeffs, bins=100)
        hist = hist / np.sum(hist)
        
        # Look for double peaks around zero (sign of double quantization)
        center_idx = len(hist) // 2
        center_region = hist[center_idx-10:center_idx+10]
        
        # Measure peakiness around zero
        zero_peak_strength = np.max(center_region) / (np.mean(hist) + 1e-10)
        
        return min(zero_peak_strength, 10.0)
    
    def _benford_law_analysis(self, gray: np.ndarray) -> float:
        """Apply Benford's law to DCT coefficients"""
        h, w = gray.shape
        first_digits = []
        
        # Extract DCT coefficients
        for i in range(0, h-8, 8):
            for j in range(0, w-8, 8):
                block = gray[i:i+8, j:j+8].astype(np.float32)
                dct_block = cv2.dct(block)
                
                # Get first digits of non-zero coefficients
                for coeff in dct_block.flatten():
                    if abs(coeff) >= 1:
                        first_digit = int(str(int(abs(coeff)))[0])
                        if 1 <= first_digit <= 9:
                            first_digits.append(first_digit)
        
        if len(first_digits) < 100:  # Not enough data
            return 0.0
        
        # Expected Benford distribution
        benford_expected = np.array([np.log10(1 + 1/d) for d in range(1, 10)])
        
        # Observed distribution
        observed_counts = np.bincount(first_digits, minlength=10)[1:10]
        observed_dist = observed_counts / np.sum(observed_counts)
        
        # Chi-square test for deviation from Benford's law
        chi_square = np.sum((observed_dist - benford_expected)**2 / benford_expected)
        
        return chi_square
    
    def _detect_blocking_inconsistency(self, gray: np.ndarray) -> float:
        """Detect inconsistent blocking patterns (sign of double compression)"""
        # Measure blocking at different grid alignments
        blocking_scores = []
        
        for offset_x in range(0, 8, 2):
            for offset_y in range(0, 8, 2):
                # Shift the analysis grid
                shifted_gray = gray[offset_y:, offset_x:]
                if shifted_gray.shape[0] > 16 and shifted_gray.shape[1] > 16:
                    blocking = self._detect_grid_blocking(shifted_gray)
                    blocking_scores.append(blocking)
        
        # Inconsistent blocking suggests double compression
        if len(blocking_scores) > 1:
            inconsistency = np.std(blocking_scores) / (np.mean(blocking_scores) + 1e-10)
        else:
            inconsistency = 0
        
        return inconsistency
    
    def _detect_compression_inconsistency(self, image: np.ndarray) -> Dict[str, float]:
        """Detect compression inconsistencies across image regions"""
        features = {}
        
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Divide image into regions and analyze compression separately
        h, w = gray.shape
        region_size = min(h, w) // 4
        
        compression_scores = []
        for i in range(0, h-region_size, region_size//2):
            for j in range(0, w-region_size, region_size//2):
                region = gray[i:i+region_size, j:j+region_size]
                
                # Analyze compression in this region
                blocking = self._detect_grid_blocking(region)
                compression_scores.append(blocking)
        
        # Measure inconsistency across regions
        if len(compression_scores) > 1:
            features['regional_inconsistency'] = np.std(compression_scores)
            features['max_compression_diff'] = np.max(compression_scores) - np.min(compression_scores)
        else:
            features['regional_inconsistency'] = 0
            features['max_compression_diff'] = 0
        
        return features
    
    def _analyze_dct_coefficients(self, gray: np.ndarray) -> Dict[str, float]:
        """Comprehensive DCT coefficient analysis"""
        features = {}
        
        h, w = gray.shape
        all_ac_coeffs = []
        dc_coeffs = []
        
        # Process all 8x8 blocks
        for i in range(0, h-8, 8):
            for j in range(0, w-8, 8):
                block = gray[i:i+8, j:j+8].astype(np.float32)
                dct_block = cv2.dct(block)
                
                # DC coefficient
                dc_coeffs.append(dct_block[0, 0])
                
                # AC coefficients
                ac_coeffs = dct_block[dct_block != dct_block[0, 0]]
                all_ac_coeffs.extend(ac_coeffs)
        
        all_ac_coeffs = np.array(all_ac_coeffs)
        dc_coeffs = np.array(dc_coeffs)
        
        # DC coefficient analysis
        features['dc_variance'] = np.var(dc_coeffs)
        features['dc_range'] = np.max(dc_coeffs) - np.min(dc_coeffs)
        
        # AC coefficient analysis
        features['ac_sparsity'] = np.sum(np.abs(all_ac_coeffs) < 1) / len(all_ac_coeffs)
        features['ac_energy'] = np.mean(all_ac_coeffs**2)
        features['ac_kurtosis'] = self._compute_kurtosis(all_ac_coeffs)
        
        return features
    
    def _detect_frequency_artifacts(self, gray: np.ndarray) -> Dict[str, float]:
        """Detect frequency domain compression artifacts"""
        features = {}
        
        # 2D FFT
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shift)
        
        # Look for compression-related frequency patterns
        # JPEG compression affects specific frequency bands
        
        # High frequency suppression (typical in compressed images)
        h, w = magnitude.shape
        center_h, center_w = h//2, w//2
        
        # Create frequency masks
        y, x = np.ogrid[:h, :w]
        
        # Low frequency region
        low_freq_mask = (x - center_w)**2 + (y - center_h)**2 <= (min(h,w)//8)**2
        low_freq_energy = np.mean(magnitude[low_freq_mask])
        
        # High frequency region
        high_freq_mask = (x - center_w)**2 + (y - center_h)**2 >= (min(h,w)//4)**2
        high_freq_energy = np.mean(magnitude[high_freq_mask])
        
        # Frequency ratio
        features['freq_ratio'] = high_freq_energy / (low_freq_energy + 1e-10)
        
        # Frequency domain blocking artifacts
        freq_blocking = self._detect_frequency_blocking(magnitude)
        features['freq_blocking'] = freq_blocking
        
        return features
    
    def _detect_frequency_blocking(self, magnitude: np.ndarray) -> float:
        """Detect blocking artifacts in frequency domain"""
        # JPEG blocking creates cross-shaped patterns in frequency domain
        h, w = magnitude.shape
        center_h, center_w = h//2, w//2
        
        # Extract cross-shaped regions
        horizontal_line = magnitude[center_h, :]
        vertical_line = magnitude[:, center_w]
        
        # Look for periodic patterns (8-pixel blocking creates specific frequencies)
        blocking_freq = w // 8  # Frequency corresponding to 8-pixel blocks
        
        if blocking_freq < len(horizontal_line)//2:
            h_blocking_strength = horizontal_line[center_w + blocking_freq] + horizontal_line[center_w - blocking_freq]
            v_blocking_strength = vertical_line[center_h + blocking_freq] + vertical_line[center_h - blocking_freq]
            
            avg_strength = (h_blocking_strength + v_blocking_strength) / 2
            return avg_strength / (np.mean(magnitude) + 1e-10)
        
        return 0.0
    
    def _detect_ringing_artifacts(self, gray: np.ndarray) -> Dict[str, float]:
        """Detect ringing artifacts around edges"""
        features = {}
        
        # Detect edges
        edges = cv2.Canny(gray.astype(np.uint8), 50, 150)
        
        # Dilate edges to create edge regions
        kernel = np.ones((5,5), np.uint8)
        edge_regions = cv2.dilate(edges, kernel, iterations=1)
        
        # Analyze intensity variations near edges
        edge_pixels = np.where(edge_regions > 0)
        
        if len(edge_pixels[0]) > 0:
            # Sample regions around edges
            ringing_scores = []
            
            for i in range(0, len(edge_pixels[0]), 10):  # Sample every 10th edge pixel
                y, x = edge_pixels[0][i], edge_pixels[1][i]
                
                # Extract small region around edge pixel
                if (y >= 5 and y < gray.shape[0]-5 and 
                    x >= 5 and x < gray.shape[1]-5):
                    
                    region = gray[y-5:y+5, x-5:x+5]
                    
                    # Measure oscillations (ringing)
                    # Apply high-pass filter to detect oscillations
                    high_pass_kernel = np.array([[-1, -1, -1], 
                                               [-1, 8, -1], 
                                               [-1, -1, -1]])
                    
                    filtered = convolve2d(region, high_pass_kernel, mode='valid')
                    ringing_score = np.std(filtered)
                    ringing_scores.append(ringing_score)
            
            features['ringing_strength'] = np.mean(ringing_scores) if ringing_scores else 0
            features['ringing_variance'] = np.var(ringing_scores) if ringing_scores else 0
        else:
            features['ringing_strength'] = 0
            features['ringing_variance'] = 0
        
        return features
    
    # Helper methods
    def _create_blocking_kernels(self) -> List[np.ndarray]:
        """Create kernels for detecting blocking artifacts"""
        kernels = []
        
        # Horizontal blocking detection kernel
        h_kernel = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ])
        
        # Vertical blocking detection kernel
        v_kernel = h_kernel.T
        
        kernels.extend([h_kernel, v_kernel])
        
        return kernels
    
    def _measure_bimodality(self, histogram: np.ndarray) -> float:
        """Measure bimodality of a histogram"""
        # Find peaks
        peaks = []
        for i in range(1, len(histogram)-1):
            if (histogram[i] > histogram[i-1] and 
                histogram[i] > histogram[i+1] and
                histogram[i] > 0.01):  # Minimum peak height
                peaks.append((i, histogram[i]))
        
        if len(peaks) >= 2:
            # Sort by height
            peaks.sort(key=lambda x: x[1], reverse=True)
            
            # Take two highest peaks
            peak1_pos, peak1_height = peaks[0]
            peak2_pos, peak2_height = peaks[1]
            
            # Measure separation and height ratio
            separation = abs(peak1_pos - peak2_pos) / len(histogram)
            height_ratio = min(peak1_height, peak2_height) / max(peak1_height, peak2_height)
            
            # Bimodality score
            bimodality = separation * height_ratio
            return bimodality
        
        return 0.0
    
    def _compute_kurtosis(self, data: np.ndarray) -> float:
        """Compute kurtosis of data"""
        if len(data) == 0:
            return 0.0
        
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return 0.0
        
        normalized = (data - mean) / std
        kurtosis = np.mean(normalized**4) - 3  # Excess kurtosis
        
        return kurtosis

class CompressionFeatureExtractor(nn.Module):
    """Neural network module for compression artifact detection"""
    
    def __init__(self, feature_dim: int = 256):
        super().__init__()
        
        self.compression_detector = CompressionArtifactDetector()
        
        # Neural network for learning compression patterns
        self.conv_layers = nn.Sequential(
            # Focus on 8x8 block patterns
            nn.Conv2d(1, 32, kernel_size=8, stride=8, padding=0),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            
            nn.AdaptiveAvgPool2d((1, 1))
        )
        
        # Feature fusion
        self.feature_fusion = nn.Sequential(
            nn.Linear(128 + 50, feature_dim),  # 50 handcrafted compression features
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(feature_dim, feature_dim)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.size(0)
        
        # Convert to grayscale for compression analysis
        if x.size(1) == 3:
            gray = 0.299 * x[:, 0:1] + 0.587 * x[:, 1:2] + 0.114 * x[:, 2:3]
        else:
            gray = x
        
        # CNN features
        cnn_features = self.conv_layers(gray)
        cnn_features = cnn_features.view(batch_size, -1)
        
        # Handcrafted compression features
        compression_features = []
        for i in range(batch_size):
            img_np = (gray[i, 0].cpu().numpy() * 255).astype(np.uint8)
            
            artifacts = self.compression_detector.detect_all_artifacts(img_np)
            
            # Convert to feature vector
            feature_vector = [
                artifacts.get('h_blocking', 0),
                artifacts.get('v_blocking', 0),
                artifacts.get('avg_blocking', 0),
                artifacts.get('grid_blocking', 0),
                artifacts.get('blocking_strength', 0),
                artifacts.get('dct_quantization', 0),
                artifacts.get('hist_quantization', 0),
                artifacts.get('local_var_pattern', 0),
                artifacts.get('dct_double_compression', 0),
                artifacts.get('benford_violation', 0),
                artifacts.get('blocking_inconsistency', 0),
                artifacts.get('regional_inconsistency', 0),
                artifacts.get('max_compression_diff', 0),
                artifacts.get('dc_variance', 0),
                artifacts.get('dc_range', 0),
                artifacts.get('ac_sparsity', 0),
                artifacts.get('ac_energy', 0),
                artifacts.get('ac_kurtosis', 0),
                artifacts.get('freq_ratio', 0),
                artifacts.get('freq_blocking', 0),
                artifacts.get('ringing_strength', 0),
                artifacts.get('ringing_variance', 0)
            ]
            
            # Pad to fixed size
            while len(feature_vector) < 50:
                feature_vector.append(0.0)
            
            compression_features.append(feature_vector[:50])
        
        compression_features = torch.tensor(
            np.array(compression_features),
            dtype=torch.float32,
            device=x.device
        )
        
        # Combine features
        combined_features = torch.cat([cnn_features, compression_features], dim=1)
        output = self.feature_fusion(combined_features)
        
        return output
