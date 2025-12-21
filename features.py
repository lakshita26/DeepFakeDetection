import cv2
import numpy as np
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import torch
import torch.nn as nn
from efficientnet_pytorch import EfficientNet
import json
from pathlib import Path

class LBPHExtractor:
    def __init__(self, config):
        self.radius = config['features']['lbph']['radius']
        self.neighbors = config['features']['lbph']['neighbors']
        self.grid_x = config['features']['lbph']['grid_x']
        self.grid_y = config['features']['lbph']['grid_y']
    
    def extract_lbp(self, image):
        """Extract Local Binary Pattern"""
        def get_pixel(img, center, x, y):
            new_value = 0
            try:
                if img[x][y] >= center:
                    new_value = 1
            except:
                pass
            return new_value
        
        lbp_image = np.zeros_like(image)
        
        for i in range(self.radius, image.shape[0] - self.radius):
            for j in range(self.radius, image.shape[1] - self.radius):
                center = image[i][j]
                val_ar = []
                
                # 8-neighborhood
                val_ar.append(get_pixel(image, center, i-1, j-1))     # top_left
                val_ar.append(get_pixel(image, center, i-1, j))       # top
                val_ar.append(get_pixel(image, center, i-1, j+1))     # top_right
                val_ar.append(get_pixel(image, center, i, j+1))       # right
                val_ar.append(get_pixel(image, center, i+1, j+1))     # bottom_right
                val_ar.append(get_pixel(image, center, i+1, j))       # bottom
                val_ar.append(get_pixel(image, center, i+1, j-1))     # bottom_left
                val_ar.append(get_pixel(image, center, i, j-1))       # left
                
                # Convert to decimal
                power_val = [1, 2, 4, 8, 16, 32, 64, 128]
                val = sum([val_ar[i] * power_val[i] for i in range(8)])
                lbp_image[i][j] = val
        
        return lbp_image
    
    def extract_histogram(self, lbp_image):
        """Extract histogram from LBP image with spatial grid"""
        h, w = lbp_image.shape
        grid_h = h // self.grid_y
        grid_w = w // self.grid_x
        
        histograms = []
        
        for i in range(self.grid_y):
            for j in range(self.grid_x):
                # Extract grid cell
                y1, y2 = i * grid_h, (i + 1) * grid_h
                x1, x2 = j * grid_w, (j + 1) * grid_w
                cell = lbp_image[y1:y2, x1:x2]
                
                # Compute histogram
                hist, _ = np.histogram(cell.ravel(), bins=256, range=(0, 256))
                hist = hist.astype(np.float32)
                hist = hist / (hist.sum() + 1e-7)  # Normalize
                
                histograms.append(hist)
        
        return np.concatenate(histograms)
    
    def extract_features(self, image):
        """Extract LBPH features"""
        lbp_image = self.extract_lbp(image)
        features = self.extract_histogram(lbp_image)
        return features

class FisherfaceExtractor:
    def __init__(self, config):
        self.n_components = config['features']['fisherface']['n_components']
        self.pca_components = config['features']['fisherface']['pca_components']
        self.pca = None
        self.lda = None
        self.is_fitted = False
    
    def fit(self, X, y):
        """Fit PCA + LDA"""
        # Flatten images
        X_flat = X.reshape(X.shape[0], -1)
        
        # PCA first
        self.pca = PCA(n_components=self.pca_components, whiten=True)
        X_pca = self.pca.fit_transform(X_flat)
        
        # LDA second
        self.lda = LinearDiscriminantAnalysis(n_components=self.n_components)
        self.lda.fit(X_pca, y)
        
        self.is_fitted = True
    
    def transform(self, X):
        """Transform images to Fisherface features"""
        if not self.is_fitted:
            raise ValueError("Extractor must be fitted first")
        
        X_flat = X.reshape(X.shape[0], -1)
        X_pca = self.pca.transform(X_flat)
        X_lda = self.lda.transform(X_pca)
        
        return X_lda
    
    def extract_features(self, image):
        """Extract features from single image"""
        if not self.is_fitted:
            raise ValueError("Extractor must be fitted first")
        
        X = image.reshape(1, -1)
        X_pca = self.pca.transform(X)
        X_lda = self.lda.transform(X_pca)
        
        return X_lda.flatten()

class EfficientNetExtractor(nn.Module):
    def __init__(self, config):
        super().__init__()
        model_name = config['features']['efficientnet']['model_name']
        pretrained = config['features']['efficientnet']['pretrained']
        
        # Load EfficientNet
        self.backbone = EfficientNet.from_pretrained(model_name) if pretrained else EfficientNet.from_name(model_name)
        
        # Remove classifier
        self.backbone._fc = nn.Identity()
        
        # Feature dimension
        self.feature_dim = config['features']['efficientnet']['feature_dim']
    
    def forward(self, x):
        """Extract features"""
        features = self.backbone(x)
        return features
    
    def extract_features(self, image):
        """Extract features from single image"""
        self.eval()
        with torch.no_grad():
            if len(image.shape) == 3:
                image = image.unsqueeze(0)  # Add batch dimension
            
            # Convert to tensor if needed
            if not isinstance(image, torch.Tensor):
                image = torch.from_numpy(image).float()
            
            features = self.forward(image)
            return features.cpu().numpy().flatten()

class FeatureExtractor:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize extractors
        self.lbph_extractor = LBPHExtractor(self.config)
        self.fisherface_extractor = FisherfaceExtractor(self.config)
        self.efficientnet_extractor = EfficientNetExtractor(self.config)
        
        try:
            from models.gan_detector import GANArtifactDetector
            from models.diffusion_detector import DiffusionForensicsExtractor
            
            self.gan_detector = GANArtifactDetector()
            self.diffusion_detector = DiffusionForensicsExtractor()
            self.use_advanced_models = True
        except ImportError:
            print("Warning: GAN and Diffusion models not available")
            self.use_advanced_models = False
    
    def fit_classical_extractors(self, gray_images, labels):
        """Fit classical feature extractors"""
        print("Fitting Fisherface extractor...")
        self.fisherface_extractor.fit(gray_images, labels)
    
    def extract_all_features(self, normalized_image, gray_image, image_array=None):
        """Extract all features from both image paths"""
        # Classical features from grayscale
        lbph_features = self.lbph_extractor.extract_features(gray_image)
        fisherface_features = self.fisherface_extractor.extract_features(gray_image)
        
        # Deep features from normalized
        efficientnet_features = self.efficientnet_extractor.extract_features(normalized_image)
        
        gan_features = None
        diffusion_features = None
        
        if self.use_advanced_models and image_array is not None:
            try:
                gan_features = self.gan_detector.extract_gan_artifacts(image_array)
                diffusion_features = self.diffusion_detector.extract_diffusion_artifacts(image_array)
            except Exception as e:
                print(f"Error extracting advanced features: {e}")
                # Fallback to zero vectors
                gan_features = np.zeros(512, dtype=np.float32)
                diffusion_features = np.zeros(512, dtype=np.float32)
        else:
            # Fallback for when advanced models not available
            gan_features = np.zeros(512, dtype=np.float32)
            diffusion_features = np.zeros(512, dtype=np.float32)
        
        return {
            'lbph': lbph_features,
            'fisherface': fisherface_features,
            'efficientnet': efficientnet_features,
            'gan': gan_features,
            'diffusion': diffusion_features
        }
    
    def save_extractors(self, save_dir):
        """Save fitted extractors"""
        save_dir = Path(save_dir)
        save_dir.mkdir(exist_ok=True)
        
        # Save Fisherface components
        if self.fisherface_extractor.is_fitted:
            np.save(save_dir / "pca_components.npy", self.fisherface_extractor.pca.components_)
            np.save(save_dir / "pca_mean.npy", self.fisherface_extractor.pca.mean_)
            np.save(save_dir / "lda_scalings.npy", self.fisherface_extractor.lda.scalings_)
            np.save(save_dir / "lda_means.npy", self.fisherface_extractor.lda.means_)
        
        # Save EfficientNet
        torch.save(self.efficientnet_extractor.state_dict(), save_dir / "efficientnet.pth")
    
    def load_extractors(self, save_dir):
        """Load fitted extractors"""
        save_dir = Path(save_dir)
        
        # Load Fisherface components
        if (save_dir / "pca_components.npy").exists():
            self.fisherface_extractor.pca = PCA()
            self.fisherface_extractor.pca.components_ = np.load(save_dir / "pca_components.npy")
            self.fisherface_extractor.pca.mean_ = np.load(save_dir / "pca_mean.npy")
            
            self.fisherface_extractor.lda = LinearDiscriminantAnalysis()
            self.fisherface_extractor.lda.scalings_ = np.load(save_dir / "lda_scalings.npy")
            self.fisherface_extractor.lda.means_ = np.load(save_dir / "lda_means.npy")
            
            self.fisherface_extractor.is_fitted = True
        
        # Load EfficientNet
        if (save_dir / "efficientnet.pth").exists():
            self.efficientnet_extractor.load_state_dict(torch.load(save_dir / "efficientnet.pth"))

if __name__ == "__main__":
    extractor = FeatureExtractor()
    print("Feature extractors initialized successfully!")
