#!/usr/bin/env python3
"""
Simple hello world test for the artwork identifier environment
"""

import torch
import cv2
import transformers
import fastapi
from src.utils import setup_logging, get_logger
from config import get_config

def main():
    # Setup logging
    config = get_config()
    setup_logging(**config["logging"])
    logger = get_logger(__name__)
    
    print("\n🎨 Artwork Identifier - Environment Test")
    print("=" * 50)
    
    # Test imports
    print("\n✅ Core dependencies loaded successfully:")
    print(f"  - PyTorch version: {torch.__version__}")
    print(f"  - OpenCV version: {cv2.__version__}")
    print(f"  - Transformers version: {transformers.__version__}")
    print(f"  - FastAPI version: {fastapi.__version__}")
    print(f"  - Device: {config['processing']['device']}")
    
    # Test CUDA availability
    if torch.cuda.is_available():
        print(f"  - CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        print("  - CUDA: Not available (CPU mode)")
    
    # Test logging
    logger.info("Hello World! Artwork Identifier is ready.")
    
    print("\n🚀 Environment setup complete! Ready for artwork identification.")
    print("=" * 50)

if __name__ == "__main__":
    main()