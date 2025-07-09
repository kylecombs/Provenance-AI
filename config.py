import os
from pathlib import Path
from typing import Dict, Any
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Data subdirectories
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ANNOTATIONS_DIR = DATA_DIR / "annotations"

# Model configuration
MODEL_CONFIG = {
    "detection": {
        "model_name": "yolov8x",  # YOLOv8 extra large model
        "confidence_threshold": 0.25,
        "nms_threshold": 0.45,
        "max_detections": 100
    },
    "feature_extraction": {
        "model_name": "clip-vit-large-patch14",
        "batch_size": 32,
        "embedding_dim": 768
    },
    "matching": {
        "similarity_threshold": 0.85,
        "top_k": 10,
        "index_type": "IVF1024,Flat",  # FAISS index type
        "nprobe": 10
    }
}

# Database configuration
DATABASE_CONFIG = {
    "url": os.getenv("DATABASE_URL", "sqlite:///artwork_db.sqlite"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "artwork_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# API configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "reload": True,
    "max_upload_size": 50 * 1024 * 1024,  # 50MB
    "allowed_extensions": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]
}

# Logging configuration
LOGGING_CONFIG = {
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "log_to_console": True,
    "log_to_file": True,
    "log_dir": str(LOGS_DIR)
}

# Processing configuration
PROCESSING_CONFIG = {
    "image_size": (1024, 1024),  # Target size for processing
    "batch_size": 16,
    "num_workers": 4,
    "device": "cuda" if os.getenv("USE_GPU", "true").lower() == "true" else "cpu"
}


def load_config_from_yaml(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file if exists.
    """
    if config_path is None:
        config_path = BASE_DIR / "config.yaml"
    
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    return {}


def get_config() -> Dict[str, Any]:
    """
    Get complete configuration, merging defaults with YAML config.
    """
    yaml_config = load_config_from_yaml()
    
    config = {
        "paths": {
            "base_dir": str(BASE_DIR),
            "data_dir": str(DATA_DIR),
            "models_dir": str(MODELS_DIR),
            "logs_dir": str(LOGS_DIR),
            "raw_data_dir": str(RAW_DATA_DIR),
            "processed_data_dir": str(PROCESSED_DATA_DIR),
            "annotations_dir": str(ANNOTATIONS_DIR)
        },
        "model": MODEL_CONFIG,
        "database": DATABASE_CONFIG,
        "api": API_CONFIG,
        "logging": LOGGING_CONFIG,
        "processing": PROCESSING_CONFIG
    }
    
    # Merge with YAML config if exists
    if yaml_config:
        for key, value in yaml_config.items():
            if key in config and isinstance(config[key], dict):
                config[key].update(value)
            else:
                config[key] = value
    
    return config