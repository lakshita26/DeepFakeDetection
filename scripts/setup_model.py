#!/usr/bin/env python3
"""
Setup script to initialize the model and create necessary directories
"""
import os
import json
import torch
import numpy as np
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from model import HybridDeepfakeDetector

def setup_model():
    """Initialize model structure and create necessary directories"""
    
    # Create necessary directories
    directories = [
        'models',
        'uploads',
        'uploads/gradcam',
        'data/processed'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Load configuration
    config_path = 'config.json'
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Initialize model architecture
    model = HybridDeepfakeDetector(
        classical_dim=config['model']['classical_features_dim'],
        efficientnet_model=config['model']['efficientnet_model']
    )
    
    # Create a dummy model checkpoint if none exists
    model_path = 'models/hybrid_model.pth'
    if not os.path.exists(model_path):
        print("Creating dummy model checkpoint...")
        
        # Initialize with random weights for demo purposes
        checkpoint = {
            'model_state_dict': model.state_dict(),
            'epoch': 0,
            'best_accuracy': 0.5,
            'config': config
        }
        
        torch.save(checkpoint, model_path)
        print(f"Created model checkpoint: {model_path}")
    
    # Create dummy PCA and LDA models for demo
    import joblib
    from sklearn.decomposition import PCA
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    
    if not os.path.exists('models/pca_model.pkl'):
        # Create dummy PCA
        dummy_data = np.random.randn(100, config['model']['classical_features_dim'])
        pca = PCA(n_components=min(50, config['model']['classical_features_dim']))
        pca.fit(dummy_data)
        joblib.dump(pca, 'models/pca_model.pkl')
        print("Created dummy PCA model")
    
    if not os.path.exists('models/lda_model.pkl'):
        # Create dummy LDA
        dummy_data = np.random.randn(100, 50)
        dummy_labels = np.random.randint(0, 2, 100)
        lda = LinearDiscriminantAnalysis()
        lda.fit(dummy_data, dummy_labels)
        joblib.dump(lda, 'models/lda_model.pkl')
        print("Created dummy LDA model")
    
    print("Model setup completed successfully!")
    return True

if __name__ == '__main__':
    setup_model()
