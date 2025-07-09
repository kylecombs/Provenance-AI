#!/usr/bin/env python3
"""
Quick database test to verify setup
"""

from src.database import get_db, test_connection, get_db_info
from src.database import ArtworkCRUD, ExhibitionCRUD, InstallationPhotoCRUD, ArtworkAppearanceCRUD
from src.utils import setup_logging, get_logger
from config import get_config

def main():
    # Setup logging
    config = get_config()
    setup_logging(**config["logging"])
    logger = get_logger(__name__)
    
    print("🎨 Artwork Identifier Database Test")
    print("=" * 40)
    
    # Test connection
    print("\n1. Testing database connection...")
    if test_connection():
        print("✅ Database connection successful")
        
        # Get database info
        db_info = get_db_info()
        print(f"   Database: {db_info.get('version', 'Unknown')}")
    else:
        print("❌ Database connection failed")
        return False
    
    # Test CRUD operations
    print("\n2. Testing CRUD operations...")
    try:
        with get_db() as db:
            artwork_crud = ArtworkCRUD()
            
            # Count existing artworks
            artworks = artwork_crud.get_all(db)
            print(f"   Found {len(artworks)} artworks in database")
            
            # Search for Van Gogh
            van_gogh_works = artwork_crud.search_by_artist(db, "Van Gogh")
            print(f"   Found {len(van_gogh_works)} Van Gogh works")
            
            if van_gogh_works:
                artwork = van_gogh_works[0]
                print(f"   Sample artwork: '{artwork.title}' by {artwork.artist}")
                
        print("✅ CRUD operations successful")
        
    except Exception as e:
        print(f"❌ CRUD operations failed: {e}")
        return False
    
    # Test statistics
    print("\n3. Testing statistics...")
    try:
        with get_db() as db:
            appearance_crud = ArtworkAppearanceCRUD()
            stats = appearance_crud.get_statistics(db)
            print(f"   Total appearances: {stats['total_appearances']}")
            print(f"   Verification rate: {stats['verification_rate']:.1%}")
            print(f"   Average confidence: {stats['average_confidence']:.2f}")
            
        print("✅ Statistics successful")
        
    except Exception as e:
        print(f"❌ Statistics failed: {e}")
        return False
    
    print("\n🚀 All database tests passed!")
    print("Database setup is complete and working correctly.")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)