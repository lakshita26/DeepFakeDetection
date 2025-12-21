import cv2
import numpy as np
from scipy import ndimage
from skimage.feature import local_binary_pattern, graycomatrix, graycoprops
from skimage.filters import gabor
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict, List
import dlib
from scipy.spatial.distance import euclidean

class AdvancedFeatureExtractor:
    """Enhanced feature extraction with temporal consistency and micro-expression analysis"""
    
    def __init__(self, image_size: int = 224):
        self.image_size = image_size
        self.face_detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = None  # Will be loaded if available
        
    def extract_comprehensive_features(self, image: np.ndarray, 
                                     previous_frame: np.ndarray = None) -> Dict[str, np.ndarray]:
        """Extract all advanced features including temporal consistency"""
        features = {}
        
        # Convert to different color spaces
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
        
        features['frequency_advanced'] = self._extract_advanced_frequency_features(gray)
        
        features['face_geometry'] = self._extract_face_geometry_features(image, gray)
        
        features['micro_expressions'] = self._extract_micro_expression_features(gray)
        
        features['skin_texture'] = self._extract_skin_texture_features(image, gray)
        
        features['multi_resolution'] = self._extract_multi_resolution_features(gray)
        
        if previous_frame is not None:
            features['temporal'] = self._extract_temporal_features(image, previous_frame)
        
        features['compression_advanced'] = self._extract_advanced_compression_features(gray)
        
        return features
    
    def _extract_advanced_frequency_features(self, gray: np.ndarray) -> np.ndarray:
        """Advanced frequency domain analysis with DCT coefficient analysis"""
        features = []
        
        dct = cv2.dct(gray.astype(np.float32))
        
        # Extract DCT coefficient statistics
        dct_ac = dct[1:, 1:]  # AC coefficients
        features.extend([
            np.mean(np.abs(dct_ac)),
            np.std(dct_ac),
            np.percentile(np.abs(dct_ac), 90),
            np.sum(np.abs(dct_ac) > np.percentile(np.abs(dct_ac), 95))
        ])
        
        benford_score = self._compute_benford_score(dct_ac.flatten())
        features.append(benford_score)
        
        spectral_residual = self._compute_spectral_residual(gray)
        features.extend([
            np.mean(spectral_residual),
            np.std(spectral_residual),
            np.max(spectral_residual)
        ])
        
        for scale in [0.5, 1.0, 2.0]:
            if scale != 1.0:
                h, w = int(gray.shape[0] * scale), int(gray.shape[1] * scale)
                scaled = cv2.resize(gray, (w, h))
            else:
                scaled = gray
                
            fft = np.fft.fft2(scaled)
            magnitude = np.abs(fft)
            features.extend([
                np.mean(magnitude),
                np.std(magnitude),
                self._compute_high_freq_ratio(magnitude)
            ])
        
        return np.array(features)
    
    def _extract_face_geometry_features(self, image: np.ndarray, gray: np.ndarray) -> np.ndarray:
        """Extract facial landmark consistency features"""
        features = []
        
        faces = self.face_detector(gray)
        
        if len(faces) > 0:
            face = faces[0]  # Use first detected face
            
            face_roi = gray[face.top():face.bottom(), face.left():face.right()]
            if face_roi.size > 0:
                symmetry_score = self._compute_face_symmetry(face_roi)
                features.append(symmetry_score)
                
                eye_features = self._analyze_eye_regions(face_roi)
                features.extend(eye_features)
                
                mouth_features = self._analyze_mouth_region(face_roi)
                features.extend(mouth_features)
            else:
                features.extend([0.0] * 10)  # Default values if no face
        else:
            features.extend([0.0] * 10)  # Default values if no face detected
        
        face_confidence = len(faces) / max(1, len(faces))  # Normalized
        features.append(face_confidence)
        
        return np.array(features)
    
    def _extract_micro_expression_features(self, gray: np.ndarray) -> np.ndarray:
        """Extract micro-expression analysis features"""
        features = []
        
        # Simulate micro-expression detection with texture analysis
        
        # Multi-scale texture analysis for subtle changes
        for window_size in [3, 5, 7]:
            kernel = np.ones((window_size, window_size), np.float32) / (window_size * window_size)
            local_mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
            local_var = cv2.filter2D((gray.astype(np.float32) - local_mean)**2, -1, kernel)
            
            features.extend([
                np.mean(local_var),
                np.std(local_var),
                np.percentile(local_var, 95)
            ])
        
        # Use gradient analysis to detect subtle muscle movements
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Compute structure tensor for motion analysis
        Jxx = cv2.GaussianBlur(grad_x * grad_x, (3, 3), 1)
        Jxy = cv2.GaussianBlur(grad_x * grad_y, (3, 3), 1)
        Jyy = cv2.GaussianBlur(grad_y * grad_y, (3, 3), 1)
        
        # Eigenvalue analysis for motion patterns
        trace = Jxx + Jyy
        det = Jxx * Jyy - Jxy * Jxy
        
        lambda1 = 0.5 * (trace + np.sqrt(np.maximum(trace**2 - 4*det, 0)))
        lambda2 = 0.5 * (trace - np.sqrt(np.maximum(trace**2 - 4*det, 0)))
        
        features.extend([
            np.mean(lambda1),
            np.mean(lambda2),
            np.std(lambda1),
            np.std(lambda2)
        ])
        
        return np.array(features)
    
    def _extract_skin_texture_features(self, image: np.ndarray, gray: np.ndarray) -> np.ndarray:
        """Advanced skin texture analysis"""
        features = []
        
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Simple skin detection mask
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        if np.sum(skin_mask) > 0:
            skin_gray = cv2.bitwise_and(gray, gray, mask=skin_mask)
            
            # Pore analysis using morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            tophat = cv2.morphologyEx(skin_gray, cv2.MORPH_TOPHAT, kernel)
            
            features.extend([
                np.mean(tophat[skin_mask > 0]) if np.sum(skin_mask) > 0 else 0,
                np.std(tophat[skin_mask > 0]) if np.sum(skin_mask) > 0 else 0
            ])
            
            laplacian = cv2.Laplacian(skin_gray, cv2.CV_64F)
            smoothness = np.var(laplacian[skin_mask > 0]) if np.sum(skin_mask) > 0 else 0
            features.append(smoothness)
            
            skin_pixels = image[skin_mask > 0]
            if len(skin_pixels) > 0:
                color_std = np.mean(np.std(skin_pixels, axis=0))
                features.append(color_std)
            else:
                features.append(0.0)
        else:
            features.extend([0.0] * 4)
        
        return np.array(features)
    
    def _extract_multi_resolution_features(self, gray: np.ndarray) -> np.ndarray:
        """Multi-resolution pyramid analysis"""
        features = []
        
        pyramid = [gray]
        current = gray
        
        for i in range(3):
            current = cv2.pyrDown(current)
            pyramid.append(current)
        
        for level, img in enumerate(pyramid):
            # Texture analysis at each level
            lbp = local_binary_pattern(img, 8, 1, method='uniform')
            hist, _ = np.histogram(lbp.ravel(), bins=10, density=True)
            
            features.extend([
                np.mean(hist),
                np.std(hist),
                np.max(hist)
            ])
            
            # Edge density at each level
            edges = cv2.Canny(img.astype(np.uint8), 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            features.append(edge_density)
        
        return np.array(features)
    
    def _extract_temporal_features(self, current: np.ndarray, previous: np.ndarray) -> np.ndarray:
        """Extract temporal consistency features"""
        features = []
        
        current_gray = cv2.cvtColor(current, cv2.COLOR_RGB2GRAY)
        previous_gray = cv2.cvtColor(previous, cv2.COLOR_RGB2GRAY)
        
        flow = cv2.calcOpticalFlowPyrLK(
            previous_gray, current_gray, 
            np.array([[100, 100]], dtype=np.float32).reshape(-1, 1, 2),
            None
        )[0]
        
        if flow is not None and len(flow) > 0:
            flow_magnitude = np.sqrt(flow[:, :, 0]**2 + flow[:, :, 1]**2)
            features.extend([
                np.mean(flow_magnitude),
                np.std(flow_magnitude)
            ])
        else:
            features.extend([0.0, 0.0])
        
        diff = cv2.absdiff(current_gray, previous_gray)
        features.extend([
            np.mean(diff),
            np.std(diff),
            np.percentile(diff, 95)
        ])
        
        grad_current = cv2.Sobel(current_gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_previous = cv2.Sobel(previous_gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_diff = np.abs(grad_current - grad_previous)
        
        features.extend([
            np.mean(grad_diff),
            np.std(grad_diff)
        ])
        
        return np.array(features)
    
    def _extract_advanced_compression_features(self, gray: np.ndarray) -> np.ndarray:
        """Advanced compression artifact detection"""
        features = []
        
        block_size = 8
        block_features = []
        
        for i in range(0, gray.shape[0] - block_size, block_size):
            for j in range(0, gray.shape[1] - block_size, block_size):
                block = gray[i:i+block_size, j:j+block_size]
                
                # DCT of block
                dct_block = cv2.dct(block.astype(np.float32))
                
                # Quantization noise estimation
                quantization_noise = np.sum(np.abs(dct_block) < 1.0) / (block_size * block_size)
                block_features.append(quantization_noise)
        
        if block_features:
            features.extend([
                np.mean(block_features),
                np.std(block_features),
                np.percentile(block_features, 90)
            ])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        double_compression_score = self._detect_double_compression(gray)
        features.append(double_compression_score)
        
        return np.array(features)
    
    def _compute_benford_score(self, coefficients: np.ndarray) -> float:
        """Compute Benford's law compliance score"""
        # Get first digits of non-zero coefficients
        non_zero = coefficients[coefficients != 0]
        if len(non_zero) == 0:
            return 0.0
            
        first_digits = []
        for coeff in non_zero:
            first_digit = int(str(abs(coeff)).replace('.', '')[0])
            if first_digit > 0:
                first_digits.append(first_digit)
        
        if len(first_digits) == 0:
            return 0.0
        
        # Expected Benford distribution
        benford_expected = [np.log10(1 + 1/d) for d in range(1, 10)]
        
        # Observed distribution
        observed = np.histogram(first_digits, bins=range(1, 11), density=True)[0]
        
        # Chi-square test
        chi_square = np.sum((observed - benford_expected)**2 / (benford_expected + 1e-10))
        return chi_square
    
    def _compute_spectral_residual(self, gray: np.ndarray) -> np.ndarray:
        """Compute spectral residual for saliency detection"""
        fft = np.fft.fft2(gray)
        log_amplitude = np.log(np.abs(fft) + 1e-10)
        phase = np.angle(fft)
        
        # Spectral residual
        spectral_residual = log_amplitude - cv2.GaussianBlur(log_amplitude, (3, 3), 1)
        
        # Inverse FFT
        fft_new = np.exp(spectral_residual + 1j * phase)
        saliency = np.abs(np.fft.ifft2(fft_new))**2
        
        return cv2.GaussianBlur(saliency, (5, 5), 2)
    
    def _compute_face_symmetry(self, face_roi: np.ndarray) -> float:
        """Compute facial symmetry score"""
        h, w = face_roi.shape
        left_half = face_roi[:, :w//2]
        right_half = cv2.flip(face_roi[:, w//2:], 1)
        
        # Resize to same dimensions
        min_width = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_width]
        right_half = right_half[:, :min_width]
        
        # Compute similarity
        diff = cv2.absdiff(left_half, right_half)
        symmetry_score = 1.0 - (np.mean(diff) / 255.0)
        
        return symmetry_score
    
    def _analyze_eye_regions(self, face_roi: np.ndarray) -> List[float]:
        """Analyze eye regions for inconsistencies"""
        h, w = face_roi.shape
        
        # Approximate eye regions (upper third, left and right quarters)
        eye_region = face_roi[:h//3, :]
        left_eye = eye_region[:, :w//4]
        right_eye = eye_region[:, 3*w//4:]
        
        features = []
        
        for eye in [left_eye, right_eye]:
            if eye.size > 0:
                # Eye texture analysis
                features.extend([
                    np.mean(eye),
                    np.std(eye),
                    cv2.Laplacian(eye, cv2.CV_64F).var()
                ])
            else:
                features.extend([0.0, 0.0, 0.0])
        
        return features
    
    def _analyze_mouth_region(self, face_roi: np.ndarray) -> List[float]:
        """Analyze mouth region for inconsistencies"""
        h, w = face_roi.shape
        
        # Approximate mouth region (lower third, center half)
        mouth_region = face_roi[2*h//3:, w//4:3*w//4]
        
        if mouth_region.size > 0:
            features = [
                np.mean(mouth_region),
                np.std(mouth_region),
                cv2.Laplacian(mouth_region, cv2.CV_64F).var()
            ]
        else:
            features = [0.0, 0.0, 0.0]
        
        return features
    
    def _compute_high_freq_ratio(self, magnitude_spectrum: np.ndarray) -> float:
        """Compute ratio of high frequency content"""
        h, w = magnitude_spectrum.shape
        center_h, center_w = h // 2, w // 2
        
        # Create high frequency mask
        y, x = np.ogrid[:h, :w]
        mask = (x - center_w)**2 + (y - center_h)**2 > (min(h, w) // 4)**2
        
        high_freq_energy = np.sum(magnitude_spectrum[mask])
        total_energy = np.sum(magnitude_spectrum)
        
        return high_freq_energy / (total_energy + 1e-10)
    
    def _detect_double_compression(self, gray: np.ndarray) -> float:
        """Detect double JPEG compression artifacts"""
        # Simulate double compression detection
        # In practice, this would analyze DCT coefficient histograms
        
        dct = cv2.dct(gray.astype(np.float32))
        
        # Look for periodic patterns in DCT coefficients
        dct_flat = dct.flatten()
        hist, bins = np.histogram(dct_flat, bins=50)
        
        # Measure histogram regularity (double compression creates regular patterns)
        hist_diff = np.diff(hist)
        regularity = np.std(hist_diff) / (np.mean(np.abs(hist_diff)) + 1e-10)
        
        return regularity
