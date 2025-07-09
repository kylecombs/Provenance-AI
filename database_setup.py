#!/usr/bin/env python3
"""
Database setup and testing script for artwork identifier
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from src.database import (
    init_db, test_connection, get_db_info, get_db,
    ArtworkCRUD, ExhibitionCRUD, InstallationPhotoCRUD, ArtworkAppearanceCRUD
)
from src.utils import setup_logging, get_logger
from config import get_config


def setup_database():
    """Initialize database tables"""
    logger = get_logger(__name__)
    logger.info("Setting up database...")
    
    try:
        init_db(drop_all=False)
        logger.info("Database setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False


def test_database_connection():
    """Test database connection"""
    logger = get_logger(__name__)
    logger.info("Testing database connection...")
    
    if test_connection():
        logger.info("Database connection successful")
        
        # Get database info
        db_info = get_db_info()
        logger.info(f"Database info: {db_info}")
        return True
    else:
        logger.error("Database connection failed")
        return False


def create_sample_data():
    """Create sample data for testing"""
    logger = get_logger(__name__)
    logger.info("Creating sample data...")
    
    try:
        with get_db() as db:
            # Initialize CRUD instances
            artwork_crud = ArtworkCRUD()
            exhibition_crud = ExhibitionCRUD()
            photo_crud = InstallationPhotoCRUD()
            appearance_crud = ArtworkAppearanceCRUD()
            
            # Check if sample artwork already exists
            existing_artwork = artwork_crud.get_by_catalog_number(db, "MoMA-472.1941")
            if existing_artwork:
                logger.info("Sample artwork already exists, using existing data")
                artwork = existing_artwork
            else:
                # Create sample artwork
                artwork = artwork_crud.create(
                    db=db,
                    title="The Starry Night",
                    artist="Vincent van Gogh",
                    width=73.7,
                    height=92.1,
                    medium="Oil on canvas",
                    creation_date="1889",
                    description="A swirling night sky over a village",
                    catalog_number="MoMA-472.1941"
                )
            
            # Check if sample exhibition already exists
            existing_exhibitions = exhibition_crud.search_by_name(db, "Van Gogh and the Colors of the Night", exact=True)
            if existing_exhibitions:
                logger.info("Sample exhibition already exists, using existing data")
                exhibition = existing_exhibitions[0]
            else:
                # Create sample exhibition
                exhibition = exhibition_crud.create(
                    db=db,
                    name="Van Gogh and the Colors of the Night",
                    museum="Museum of Modern Art",
                    gallery="Gallery 2",
                    city="New York",
                    country="USA",
                    start_date=datetime(2023, 10, 1),
                    end_date=datetime(2024, 1, 15),
                    curator="Dr. Sarah Johnson",
                    description="An exploration of Van Gogh's nocturnal masterpieces",
                    type="temporary"
                )
            
            # Check if sample photo already exists
            existing_photos = photo_crud.get_by_exhibition(db, exhibition.id)
            sample_photo = None
            for photo in existing_photos:
                if photo.original_filename == "exhibition_photo_001.jpg":
                    sample_photo = photo
                    break
            
            if sample_photo:
                logger.info("Sample photo already exists, using existing data")
                photo = sample_photo
            else:
                # Create sample installation photo
                photo = photo_crud.create(
                    db=db,
                    exhibition_id=exhibition.id,
                    image_path="/data/raw/exhibition_photo_001.jpg",
                    original_filename="exhibition_photo_001.jpg",
                    width=1920,
                    height=1080,
                    format="jpg",
                    capture_date=datetime(2023, 10, 15),
                    photographer="Museum Documentation Team",
                    room="Gallery 2",
                    view_type="overview"
                )
            
            # Check if sample appearance already exists
            existing_appearances = appearance_crud.get_by_photo(db, photo.id)
            sample_appearance = None
            for appearance in existing_appearances:
                if appearance.artwork_id == artwork.id:
                    sample_appearance = appearance
                    break
            
            if sample_appearance:
                logger.info("Sample appearance already exists, using existing data")
                appearance = sample_appearance
            else:
                # Create sample artwork appearance
                appearance = appearance_crud.create(
                    db=db,
                    artwork_id=artwork.id,
                    photo_id=photo.id,
                    bbox_x=0.2,
                    bbox_y=0.3,
                    bbox_width=0.4,
                    bbox_height=0.5,
                    detection_confidence=0.95,
                    matching_confidence=0.87,
                    visible_percentage=0.85,
                    occlusion_level="none",
                    lighting_quality="good"
                )
            
            logger.info("Sample data created successfully")
            logger.info(f"Created artwork: {artwork.title} by {artwork.artist}")
            logger.info(f"Created exhibition: {exhibition.name}")
            logger.info(f"Created photo: {photo.original_filename}")
            logger.info(f"Created appearance with {appearance.matching_confidence:.2f} confidence")
            
            return True
            
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        return False


def test_crud_operations():
    """Test basic CRUD operations"""
    logger = get_logger(__name__)
    logger.info("Testing CRUD operations...")
    
    try:
        with get_db() as db:
            artwork_crud = ArtworkCRUD()
            
            # Test search operations
            van_gogh_works = artwork_crud.search_by_artist(db, "Van Gogh")
            logger.info(f"Found {len(van_gogh_works)} Van Gogh works")
            
            starry_night = artwork_crud.search_by_title(db, "Starry Night")
            logger.info(f"Found {len(starry_night)} works with 'Starry Night' in title")
            
            # Test catalog number lookup
            artwork = artwork_crud.get_by_catalog_number(db, "MoMA-472.1941")
            if artwork:
                logger.info(f"Found artwork by catalog number: {artwork.title}")
            
            # Test statistics
            appearance_crud = ArtworkAppearanceCRUD()
            stats = appearance_crud.get_statistics(db)
            logger.info(f"Appearance statistics: {stats}")
            
            logger.info("CRUD operations test completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"CRUD operations test failed: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Database setup and testing for artwork identifier")
    parser.add_argument("--setup", action="store_true", help="Initialize database tables")
    parser.add_argument("--test", action="store_true", help="Test database connection")
    parser.add_argument("--sample-data", action="store_true", help="Create sample data")
    parser.add_argument("--test-crud", action="store_true", help="Test CRUD operations")
    parser.add_argument("--all", action="store_true", help="Run all operations")
    
    args = parser.parse_args()
    
    # Setup logging
    config = get_config()
    setup_logging(**config["logging"])
    logger = get_logger(__name__)
    
    logger.info("Starting database setup and testing")
    
    success = True
    
    if args.all or args.test:
        success &= test_database_connection()
    
    if args.all or args.setup:
        success &= setup_database()
    
    if args.all or args.sample_data:
        success &= create_sample_data()
    
    if args.all or args.test_crud:
        success &= test_crud_operations()
    
    if success:
        logger.info("All operations completed successfully")
        sys.exit(0)
    else:
        logger.error("Some operations failed")
        sys.exit(1)


if __name__ == "__main__":
    main()