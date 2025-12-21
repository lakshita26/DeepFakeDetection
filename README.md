# Deepfake Detection System

*Advanced ML-powered deepfake detection with hybrid model architecture*

[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/pgkijai301-1801s-projects/v0-image-analysis)

## Overview

An advanced deepfake detection application using a hybrid machine learning approach that combines classical computer vision techniques with deep learning. No external API subscriptions required - all models run locally.

## Features

- **Hybrid ML Model**: Combines LBPH, Fisherface, and EfficientNet-like CNN features
- **Real-time Detection**: Fast inference on uploaded images
- **Interactive UI**: Modern Next.js frontend with detailed analysis visualization
- **No API Keys Required**: Fully self-contained ML models
- **Automatic Fallback**: Gracefully degrades to heuristic analysis if ML unavailable
- **Comprehensive Metrics**: Confidence scores, uncertainty estimation, and feature importance

## Quick Start

\`\`\`bash
# 1. Install dependencies
npm install
pip install torch numpy opencv-python scikit-learn pillow

# 2. Train the ML model
python scripts/train_model.py

# 3. Run development server
npm run dev
\`\`\`

Open [http://localhost:3000](http://localhost:3000) and start detecting deepfakes!

## ML Architecture

### Model Components
- **LBPH (Local Binary Pattern Histogram)**: Texture analysis with 8x8 spatial grid
- **Fisherface**: PCA + LDA for discriminative features  
- **CNN Features**: Simplified EfficientNet-like architecture
- **Fusion Layer**: Concatenation or attention-based feature fusion
- **Classification Head**: Multi-layer perceptron with dropout and batch normalization

### Technology Stack
- **Frontend**: Next.js 16, React 19, TailwindCSS v4, Framer Motion
- **Backend**: Next.js API Routes, Node.js
- **ML**: Python, PyTorch, scikit-learn, OpenCV
- **UI**: shadcn/ui components

## Project Structure

\`\`\`
.
├── app/                    # Next.js app directory
│   ├── api/detect/        # Detection API endpoint
│   └── page.tsx           # Main application
├── components/            # React components
│   ├── upload-section.tsx
│   ├── results-section.tsx
│   └── ui/                # shadcn/ui components
├── lib/                   # Utilities
│   ├── python-ml.ts       # Python ML integration
│   └── api.ts
├── ml/                    # Machine learning
│   ├── model.py           # PyTorch model
│   ├── features.py        # Feature extractors
│   ├── train.py           # Training pipeline
│   ├── inference.py       # Inference API
│   └── config.json        # Configuration
└── scripts/               # Utility scripts
    ├── train_model.py
    └── test_model.py
\`\`\`

## Usage

### Web Interface
1. Upload an image through the web interface
2. View detailed analysis with confidence scores
3. Export analysis reports

### Command Line

**Test single image**:
\`\`\`bash
python scripts/test_model.py --image path/to/image.jpg
\`\`\`

**Batch processing**:
\`\`\`bash
python scripts/test_model.py --batch path/to/folder/
\`\`\`

**Run inference server**:
\`\`\`bash
python ml/serve.py --port 8000
\`\`\`

## Training Custom Models

1. Organize your dataset:
   \`\`\`
   ml/data/
   ├── real/
   │   └── *.jpg
   └── fake/
       └── *.jpg
   \`\`\`

2. Configure in `ml/config.json`

3. Train:
   \`\`\`bash
   python scripts/train_model.py
   \`\`\`

See [SETUP.md](./SETUP.md) for detailed instructions.

## How It Works

1. **Image Upload**: User uploads image via web interface
2. **Preprocessing**: Resized to 224x224 and normalized
3. **Feature Extraction**: LBPH, Fisherface, and CNN features
4. **Feature Fusion**: Combined via concatenation or attention
5. **Classification**: MLP predicts real/fake with confidence
6. **Display**: Shows prediction, confidence, and feature importance

## Deployment

Your project is live at:
**[https://vercel.com/pgkijai301-1801s-projects/v0-image-analysis](https://vercel.com/pgkijai301-1801s-projects/v0-image-analysis)**

Continue building on:
**[https://v0.app/chat/projects/v69b7R51teR](https://v0.app/chat/projects/v69b7R51teR)**

## Documentation

- [SETUP.md](./SETUP.md) - Complete setup guide
- [ml/README.md](./ml/README.md) - ML model documentation

## License

MIT License

