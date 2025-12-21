from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import numpy as np
import cv2
import base64
from PIL import Image
import io
import json
from pathlib import Path

from model import HybridFusionModel
from features import FeatureExtractor
from preprocess import FacePreprocessor

app = Flask(__name__)
CORS(app)

class DeepfakeDetectionAPI:
    def __init__(self, model_path="models/best_model.pth", config_path="config.json"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        try:
            from models.enhanced_hybrid_model_v2 import EnhancedHybridFusionModel
            self.model = EnhancedHybridFusionModel(config_path)
            self.use_enhanced_model = True
        except ImportError:
            from model import HybridFusionModel
            self.model = HybridFusionModel(config_path)
            self.use_enhanced_model = False
        
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        # Load optimal threshold
        try:
            with open('evaluation_results.json', 'r') as f:
                eval_results = json.load(f)
                self.optimal_threshold = eval_results['optimal_threshold']
        except:
            self.optimal_threshold = 0.5
        
        # Initialize preprocessor and feature extractor
        self.preprocessor = FacePreprocessor(config_path)
        self.feature_extractor = FeatureExtractor(config_path)
        self.feature_extractor.load_extractors("models/extractors")
        
        print(f"API initialized on device: {self.device}")
        print(f"Using enhanced model: {self.use_enhanced_model}")
        print(f"Using threshold: {self.optimal_threshold}")
    
    def preprocess_image(self, image):
        """Preprocess image for inference"""
        try:
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            normalized, gray = self.preprocessor.preprocess_image_array(opencv_image)
            
            if normalized is None:
                return None, "No face detected in image"
            
            return (normalized, gray, np.array(image)), None
            
        except Exception as e:
            return None, f"Preprocessing error: {str(e)}"
    
    def extract_features(self, processed_images):
        """Extract features from preprocessed images"""
        try:
            normalized, gray, image_array = processed_images
            features = self.feature_extractor.extract_all_features(normalized, gray, image_array)
            return features, None
            
        except Exception as e:
            return None, f"Feature extraction error: {str(e)}"
    
    def predict(self, features):
        """Make prediction with enhanced model"""
        try:
            lbph_tensor = torch.FloatTensor(features['lbph']).unsqueeze(0).to(self.device)
            fisherface_tensor = torch.FloatTensor(features['fisherface']).unsqueeze(0).to(self.device)
            efficientnet_tensor = torch.FloatTensor(features['efficientnet']).unsqueeze(0).to(self.device)
            
            if self.use_enhanced_model:
                gan_tensor = torch.FloatTensor(features['gan']).unsqueeze(0).to(self.device)
                diffusion_tensor = torch.FloatTensor(features['diffusion']).unsqueeze(0).to(self.device)
                
                with torch.no_grad():
                    probabilities, uncertainty = self.model.predict_proba(
                        lbph_tensor, fisherface_tensor, efficientnet_tensor,
                        gan_tensor, diffusion_tensor
                    )
                    
                    fake_probability = probabilities[0, 1].cpu().item()
                    uncertainty_score = uncertainty[0, 0].cpu().item()
            else:
                with torch.no_grad():
                    probabilities = self.model.predict_proba(
                        lbph_tensor, fisherface_tensor, efficientnet_tensor
                    )
                    fake_probability = probabilities[0, 1].cpu().item()
                    uncertainty_score = 1 - abs(fake_probability - 0.5) * 2
            
            is_fake = fake_probability > self.optimal_threshold
            confidence = fake_probability if is_fake else (1 - fake_probability)
            
            return {
                'is_fake': bool(is_fake),
                'fake_probability': float(fake_probability),
                'real_probability': float(1 - fake_probability),
                'confidence': float(confidence),
                'uncertainty': float(uncertainty_score),
                'threshold_used': float(self.optimal_threshold),
                'models_used': ['LBPH', 'Fisherface', 'EfficientNet', 'GAN-Detector', 'Diffusion-Detector'] if self.use_enhanced_model else ['LBPH', 'Fisherface', 'EfficientNet']
            }, None
            
        except Exception as e:
            return None, f"Prediction error: {str(e)}"

# Initialize API
detector = DeepfakeDetectionAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': True,
        'device': str(detector.device)
    })

@app.route('/predict', methods=['POST'])
def predict_image():
    """Predict if image is fake or real"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        try:
            image = Image.open(file.stream).convert('RGB')
        except Exception as e:
            return jsonify({'error': f'Invalid image format: {str(e)}'}), 400
        
        processed_images, error = detector.preprocess_image(image)
        if error:
            return jsonify({'error': error}), 400
        
        features, error = detector.extract_features(processed_images)
        if error:
            return jsonify({'error': error}), 400
        
        result, error = detector.predict(features)
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/predict_base64', methods=['POST'])
def predict_base64():
    """Predict from base64 encoded image"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(data['image'])
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
        except Exception as e:
            return jsonify({'error': f'Invalid base64 image: {str(e)}'}), 400
        
        # Preprocess image
        processed_images, error = detector.preprocess_image(image)
        if error:
            return jsonify({'error': error}), 400
        
        # Extract features
        features, error = detector.extract_features(processed_images)
        if error:
            return jsonify({'error': error}), 400
        
        # Make prediction
        result, error = detector.predict(features)
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """Predict multiple images"""
    try:
        files = request.files.getlist('images')
        
        if not files:
            return jsonify({'error': 'No images provided'}), 400
        
        results = []
        
        for i, file in enumerate(files):
            try:
                # Load image
                image = Image.open(file.stream).convert('RGB')
                
                # Preprocess image
                processed_images, error = detector.preprocess_image(image)
                if error:
                    results.append({
                        'index': i,
                        'filename': file.filename,
                        'error': error
                    })
                    continue
                
                # Extract features
                features, error = detector.extract_features(processed_images)
                if error:
                    results.append({
                        'index': i,
                        'filename': file.filename,
                        'error': error
                    })
                    continue
                
                # Make prediction
                result, error = detector.predict(features)
                if error:
                    results.append({
                        'index': i,
                        'filename': file.filename,
                        'error': error
                    })
                    continue
                
                results.append({
                    'index': i,
                    'filename': file.filename,
                    'result': result
                })
                
            except Exception as e:
                results.append({
                    'index': i,
                    'filename': file.filename,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_processed': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/model_info', methods=['GET'])
def model_info():
    """Get model information"""
    return jsonify({
        'model_type': 'Hybrid Deepfake Detection',
        'features': ['LBPH', 'Fisherface', 'EfficientNet', 'GAN-Detector', 'Diffusion-Detector'] if detector.use_enhanced_model else ['LBPH', 'Fisherface', 'EfficientNet'],
        'threshold': detector.optimal_threshold,
        'device': str(detector.device),
        'input_size': detector.config['preprocessing']['image_size']
    })

if __name__ == '__main__':
    print("Starting Deepfake Detection API...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /predict - Single image prediction")
    print("  POST /predict_base64 - Base64 image prediction")
    print("  POST /batch_predict - Batch image prediction")
    print("  GET  /model_info - Model information")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
