"""ML inference package for DeepFakeDetection

Provides simple wrappers used by scripts/test_model.py: `detect_deepfake` and
`analyze_image_detailed`.

This module is intentionally lightweight and will gracefully fall back to a
heuristic detector when heavy dependencies (torch, dlib, efficientnet, etc.)
are not available in the runtime.
"""

__all__ = ["detect_deepfake", "analyze_image_detailed"]
