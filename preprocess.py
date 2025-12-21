import cv2
import numpy as np
import dlib
import face_recognition
from pathlib import Path
import json
from tqdm import tqdm
import pandas as pd

class FacePreprocessor:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize face detector
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")
        
        self.target_size = tuple(self.config['preprocessing']['image_size'])
        
    def detect_face(self, image):
        """Detect face in image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        
        if len(faces) == 0:
            return None
        
        # Return largest face
        largest_face = max(faces, key=lambda rect: rect.width() * rect.height())
        return largest_face
    
    def get_landmarks(self, image, face_rect):
        """Get 68 facial landmarks"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        landmarks = self.predictor(gray, face_rect)
        
        points = []
        for i in range(68):
            point = landmarks.part(i)
            points.append((point.x, point.y))
        
        return np.array(points)
    
    def align_face(self, image, landmarks):
        """Align face using eye landmarks"""
        # Get eye centers
        left_eye = landmarks[36:42].mean(axis=0)
        right_eye = landmarks[42:48].mean(axis=0)
        
        # Calculate angle
        dy = right_eye[1] - left_eye[1]
        dx = right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dy, dx))
        
        # Get center point
        center = ((left_eye[0] + right_eye[0]) // 2, (left_eye[1] + right_eye[1]) // 2)
        
        # Rotate image
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        aligned = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
        
        return aligned
    
    def crop_face(self, image, face_rect, margin=0.3):
        """Crop face with margin"""
        x, y, w, h = face_rect.left(), face_rect.top(), face_rect.width(), face_rect.height()
        
        # Add margin
        margin_x = int(w * margin)
        margin_y = int(h * margin)
        
        x1 = max(0, x - margin_x)
        y1 = max(0, y - margin_y)
        x2 = min(image.shape[1], x + w + margin_x)
        y2 = min(image.shape[0], y + h + margin_y)
        
        cropped = image[y1:y2, x1:x2]
        return cropped
    
    def normalize_image(self, image):
        """Normalize image for neural networks"""
        # Resize
        resized = cv2.resize(image, self.target_size)
        
        # Convert to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalize to [0, 1]
        normalized = rgb.astype(np.float32) / 255.0
        
        # ImageNet normalization
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        normalized = (normalized - mean) / std
        
        return normalized
    
    def preprocess_image(self, image_path):
        """Complete preprocessing pipeline"""
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            return None, None
        
        # Detect face
        face_rect = self.detect_face(image)
        if face_rect is None:
            return None, None
        
        # Get landmarks
        landmarks = self.get_landmarks(image, face_rect)
        
        # Align face
        aligned = self.align_face(image, landmarks)
        
        # Crop face
        cropped = self.crop_face(aligned, face_rect)
        
        # Create dual paths
        # Path 1: Normalized for deep learning
        normalized = self.normalize_image(cropped)
        
        # Path 2: Grayscale for classical features
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        gray_resized = cv2.resize(gray, self.target_size)
        
        return normalized, gray_resized
    
    def preprocess_dataset(self, csv_path, output_dir):
        """Preprocess entire dataset"""
        df = pd.read_csv(csv_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        processed_data = []
        
        for idx, row in tqdm(df.iterrows(), total=len(df)):
            image_path = row['path']
            
            # Preprocess
            normalized, gray = self.preprocess_image(image_path)
            
            if normalized is not None:
                # Save processed images
                base_name = Path(image_path).stem
                
                # Save normalized (for deep learning)
                norm_path = output_dir / f"{base_name}_norm.npy"
                np.save(norm_path, normalized)
                
                # Save grayscale (for classical features)
                gray_path = output_dir / f"{base_name}_gray.npy"
                np.save(gray_path, gray)
                
                processed_data.append({
                    'original_path': image_path,
                    'norm_path': str(norm_path),
                    'gray_path': str(gray_path),
                    'label': row['label'],
                    'dataset': row['dataset']
                })
        
        # Save processed dataset info
        processed_df = pd.DataFrame(processed_data)
        processed_df.to_csv(output_dir / "processed_data.csv", index=False)
        
        return processed_df

if __name__ == "__main__":
    preprocessor = FacePreprocessor()
    
    # Preprocess all splits
    for split in ['train', 'val', 'test']:
        print(f"Preprocessing {split} set...")
        csv_path = f"data/{split}.csv"
        output_dir = f"data/processed/{split}"
        
        if Path(csv_path).exists():
            preprocessor.preprocess_dataset(csv_path, output_dir)
        else:
            print(f"Warning: {csv_path} not found")
