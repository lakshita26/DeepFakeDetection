#!/usr/bin/env python3
"""
Run a single-image inference through the full pipeline and print diagnostics.
Usage: python scripts/run_inference.py <image_path>
"""
import sys
import json
import numpy as np
from pathlib import Path
#!/usr/bin/env python3
"""
Lightweight inference/diagnostics script that avoids heavy dependencies.
It will run a simple pipeline (face detection with Haar cascade, crop, resize,
LBP histogram + simple stats) and print diagnostics and a heuristic "real" probability.

Usage: python scripts/run_inference.py <image_path>
"""
import sys
import json
from pathlib import Path
import numpy as np
import cv2


def extract_lbp(image, radius=1):
    h, w = image.shape
    lbp_image = np.zeros_like(image)
    for i in range(radius, h - radius):
        for j in range(radius, w - radius):
            center = image[i, j]
            vals = []
            vals.append(1 if image[i-1, j-1] >= center else 0)
            vals.append(1 if image[i-1, j] >= center else 0)
            vals.append(1 if image[i-1, j+1] >= center else 0)
            vals.append(1 if image[i, j+1] >= center else 0)
            vals.append(1 if image[i+1, j+1] >= center else 0)
            vals.append(1 if image[i+1, j] >= center else 0)
            vals.append(1 if image[i+1, j-1] >= center else 0)
            vals.append(1 if image[i, j-1] >= center else 0)
            power = [1,2,4,8,16,32,64,128]
            lbp_image[i, j] = sum([v*p for v,p in zip(vals, power)])
    return lbp_image


def lbph_histogram(gray, grid_x=8, grid_y=8):
    h, w = gray.shape
    grid_h = h // grid_y
    grid_w = w // grid_x
    histograms = []
    for i in range(grid_y):
        for j in range(grid_x):
            y1, y2 = i*grid_h, (i+1)*grid_h
            x1, x2 = j*grid_w, (j+1)*grid_w
            cell = gray[y1:y2, x1:x2]
            hist, _ = np.histogram(cell.ravel(), bins=256, range=(0,256))
            hist = hist.astype(np.float32)
            hist = hist / (hist.sum() + 1e-7)
            histograms.append(hist)
    return np.concatenate(histograms)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_inference.py <image_path>")
        sys.exit(1)

    image_path = Path(sys.argv[1])
    if not image_path.exists():
        print(f"Image not found: {image_path}")
        sys.exit(1)

    # Load image
    img_bgr = cv2.imread(str(image_path))
    if img_bgr is None:
        print("Failed to load image")
        sys.exit(1)

    # Face detection using Haar cascade (fast, no dlib required)
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    gray_full = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_full, scaleFactor=1.1, minNeighbors=4)

    if len(faces) > 0:
        x, y, w, h = faces[0]
    else:
        H, W = gray_full.shape
        x, y, w, h = W//4, H//4, W//2, H//2

    face_region = img_bgr[y:y+h, x:x+w]

    # Resize to 224x224 (config default)
    target_size = (224, 224)
    cropped = cv2.resize(face_region, target_size)

    # Normalized RGB for deep features (not using heavy libs here)
    normalized = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

    # Grayscale for classical features
    gray_face = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    # Simple stats
    stats = {
        'mean': float(np.mean(gray_face)),
        'std': float(np.std(gray_face)),
        'median': float(np.median(gray_face)),
        'min': int(np.min(gray_face)),
        'max': int(np.max(gray_face))
    }

    # LBP + LBPH histogram
    lbp = extract_lbp(gray_face)
    lbph = lbph_histogram(lbp, grid_x=8, grid_y=8)

    # Heuristic reality probability: combine stats and LBPH energy
    energy = np.sum(lbph[:256])  # coarse
    reality_prob = (stats['mean'] / 255.0) * 0.6 + (1.0 - energy) * 0.4
    reality_prob = max(0.0, min(1.0, reality_prob))

    result = {
        'image': str(image_path),
        'face_bbox': [int(x), int(y), int(w), int(h)],
        'stats': stats,
        'lbph_len': int(len(lbph)),
        'heuristic_real_probability': float(reality_prob),
        'heuristic_fake_probability': float(1.0 - reality_prob)
    }

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
