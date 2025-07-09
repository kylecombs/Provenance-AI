#!/usr/bin/env python3
"""
Artwork Identifier - Main entry point
"""

import argparse
from pathlib import Path
from src.utils import setup_logging, get_logger
from config import get_config


def main():
    """Main entry point for the artwork identifier application."""
    parser = argparse.ArgumentParser(description="AI-powered artwork identification in museum photos")
    parser.add_argument(
        "--mode",
        choices=["train", "detect", "api", "process"],
        default="api",
        help="Operation mode"
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Input file or directory path"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory path"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = get_config()
    
    # Setup logging
    setup_logging(**config["logging"])
    logger = get_logger(__name__)
    
    logger.info(f"Starting Artwork Identifier in {args.mode} mode")
    
    if args.mode == "api":
        logger.info("Starting API server...")
        # API server will be implemented in Phase 2
        print("API server functionality will be implemented in Phase 2")
    
    elif args.mode == "detect":
        if not args.input:
            logger.error("Input file required for detection mode")
            return
        logger.info(f"Running detection on: {args.input}")
        # Detection functionality will be implemented in Phase 2
        print("Detection functionality will be implemented in Phase 2")
    
    elif args.mode == "train":
        logger.info("Starting training process...")
        # Training functionality will be implemented in Phase 3
        print("Training functionality will be implemented in Phase 3")
    
    elif args.mode == "process":
        if not args.input:
            logger.error("Input directory required for processing mode")
            return
        logger.info(f"Processing images in: {args.input}")
        # Batch processing will be implemented in Phase 2
        print("Batch processing functionality will be implemented in Phase 2")


if __name__ == "__main__":
    main()