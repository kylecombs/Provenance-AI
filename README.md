# Artwork Identifier

AI-powered tool to identify artwork in museum installation photographs using computer vision and deep learning.

## Overview

This tool uses state-of-the-art object detection and image matching techniques to:
- Detect artwork in museum photographs
- Extract visual features from detected artworks
- Match detected artworks against a database of known pieces
- Provide metadata and information about identified artworks

## Installation

1. Create and activate a Python virtual environment:
```bash
python3 -m venv artwork-identifier-env
source artwork-identifier-env/bin/activate  # On Windows: artwork-identifier-env\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Project Structure

```
artwork-identifier/
├── data/                   # Data directory
│   ├── raw/               # Raw museum photos
│   ├── processed/         # Processed images
│   └── annotations/       # Annotation files
├── models/                # Trained models
├── src/                   # Source code
│   ├── detection/         # Object detection modules
│   ├── features/          # Feature extraction
│   ├── matching/          # Artwork matching
│   └── utils/             # Utilities
├── notebooks/             # Jupyter notebooks
├── tests/                 # Unit tests
├── api/                   # FastAPI application
├── config.py             # Configuration
├── main.py               # Main entry point
└── requirements.txt      # Dependencies
```

## Usage

### API Server (coming in Phase 2)
```bash
python main.py --mode api
```

### Single Image Detection (coming in Phase 2)
```bash
python main.py --mode detect --input path/to/image.jpg
```

### Batch Processing (coming in Phase 2)
```bash
python main.py --mode process --input path/to/images/ --output results/
```

### Training (coming in Phase 3)
```bash
python main.py --mode train
```

## Configuration

Configuration can be managed through:
- Environment variables in `.env`
- Configuration file `config.yaml`
- Command-line arguments

## Development Status

- [x] Phase 1: Project Setup & Environment
- [ ] Phase 2: Object Detection Implementation
- [ ] Phase 3: Feature Extraction & Matching
- [ ] Phase 4: Database Integration
- [ ] Phase 5: API Development
- [ ] Phase 6: Testing & Optimization

## License

[Your License Here]