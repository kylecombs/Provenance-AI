from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime

from .models import Artwork, Exhibition, InstallationPhoto, ArtworkAppearance
from ..utils import get_logger

logger = get_logger(__name__)


class BaseCRUD:
    """Base class for CRUD operations"""
    
    def __init__(self, model):
        self.model = model
    
    def create(self, db: Session, **kwargs) -> Any:
        """Create a new record"""
        try:
            db_obj = self.model(**kwargs)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with id: {db_obj.id}")
            return db_obj
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            db.rollback()
            raise
    
    def get_by_id(self, db: Session, id: str) -> Optional[Any]:
        """Get record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get all records with pagination"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: str, **kwargs) -> Optional[Any]:
        """Update a record"""
        try:
            db_obj = self.get_by_id(db, id)
            if not db_obj:
                return None
            
            for key, value in kwargs.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} with id: {id}")
            return db_obj
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__}: {e}")
            db.rollback()
            raise
    
    def delete(self, db: Session, id: str) -> bool:
        """Delete a record"""
        try:
            db_obj = self.get_by_id(db, id)
            if not db_obj:
                return False
            
            db.delete(db_obj)
            db.commit()
            logger.info(f"Deleted {self.model.__name__} with id: {id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__}: {e}")
            db.rollback()
            raise


class ArtworkCRUD(BaseCRUD):
    """CRUD operations for Artwork model"""
    
    def __init__(self):
        super().__init__(Artwork)
    
    def search_by_title(self, db: Session, title: str, exact: bool = False) -> List[Artwork]:
        """Search artworks by title"""
        if exact:
            return db.query(Artwork).filter(Artwork.title == title).all()
        else:
            return db.query(Artwork).filter(Artwork.title.ilike(f"%{title}%")).all()
    
    def search_by_artist(self, db: Session, artist: str, exact: bool = False) -> List[Artwork]:
        """Search artworks by artist"""
        if exact:
            return db.query(Artwork).filter(Artwork.artist == artist).all()
        else:
            return db.query(Artwork).filter(Artwork.artist.ilike(f"%{artist}%")).all()
    
    def get_by_catalog_number(self, db: Session, catalog_number: str) -> Optional[Artwork]:
        """Get artwork by catalog number"""
        return db.query(Artwork).filter(Artwork.catalog_number == catalog_number).first()
    
    def search_by_medium(self, db: Session, medium: str) -> List[Artwork]:
        """Search artworks by medium"""
        return db.query(Artwork).filter(Artwork.medium.ilike(f"%{medium}%")).all()
    
    def search_by_dimensions(self, db: Session, min_width: float = None, max_width: float = None,
                           min_height: float = None, max_height: float = None) -> List[Artwork]:
        """Search artworks by dimensions"""
        query = db.query(Artwork)
        
        if min_width is not None:
            query = query.filter(Artwork.width >= min_width)
        if max_width is not None:
            query = query.filter(Artwork.width <= max_width)
        if min_height is not None:
            query = query.filter(Artwork.height >= min_height)
        if max_height is not None:
            query = query.filter(Artwork.height <= max_height)
        
        return query.all()
    
    def get_with_appearances(self, db: Session, id: str) -> Optional[Artwork]:
        """Get artwork with all its appearances"""
        return db.query(Artwork).filter(Artwork.id == id).first()


class ExhibitionCRUD(BaseCRUD):
    """CRUD operations for Exhibition model"""
    
    def __init__(self):
        super().__init__(Exhibition)
    
    def search_by_name(self, db: Session, name: str, exact: bool = False) -> List[Exhibition]:
        """Search exhibitions by name"""
        if exact:
            return db.query(Exhibition).filter(Exhibition.name == name).all()
        else:
            return db.query(Exhibition).filter(Exhibition.name.ilike(f"%{name}%")).all()
    
    def search_by_museum(self, db: Session, museum: str) -> List[Exhibition]:
        """Search exhibitions by museum"""
        return db.query(Exhibition).filter(Exhibition.museum.ilike(f"%{museum}%")).all()
    
    def get_by_date_range(self, db: Session, start_date: datetime = None, 
                         end_date: datetime = None) -> List[Exhibition]:
        """Get exhibitions within date range"""
        query = db.query(Exhibition)
        
        if start_date:
            query = query.filter(Exhibition.end_date >= start_date)
        if end_date:
            query = query.filter(Exhibition.start_date <= end_date)
        
        return query.all()
    
    def get_current_exhibitions(self, db: Session) -> List[Exhibition]:
        """Get currently running exhibitions"""
        now = datetime.now()
        return db.query(Exhibition).filter(
            and_(Exhibition.start_date <= now, Exhibition.end_date >= now)
        ).all()
    
    def get_with_photos(self, db: Session, id: str) -> Optional[Exhibition]:
        """Get exhibition with all its photos"""
        return db.query(Exhibition).filter(Exhibition.id == id).first()


class InstallationPhotoCRUD(BaseCRUD):
    """CRUD operations for InstallationPhoto model"""
    
    def __init__(self):
        super().__init__(InstallationPhoto)
    
    def get_by_exhibition(self, db: Session, exhibition_id: str) -> List[InstallationPhoto]:
        """Get all photos for an exhibition"""
        return db.query(InstallationPhoto).filter(
            InstallationPhoto.exhibition_id == exhibition_id
        ).all()
    
    def get_unprocessed(self, db: Session) -> List[InstallationPhoto]:
        """Get all unprocessed photos"""
        return db.query(InstallationPhoto).filter(InstallationPhoto.processed == False).all()
    
    def mark_processed(self, db: Session, id: str, detection_results: dict = None) -> bool:
        """Mark photo as processed"""
        try:
            db_obj = self.get_by_id(db, id)
            if not db_obj:
                return False
            
            db_obj.processed = True
            db_obj.processing_date = datetime.now()
            if detection_results:
                db_obj.detection_results = detection_results
            
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error marking photo as processed: {e}")
            db.rollback()
            raise
    
    def search_by_photographer(self, db: Session, photographer: str) -> List[InstallationPhoto]:
        """Search photos by photographer"""
        return db.query(InstallationPhoto).filter(
            InstallationPhoto.photographer.ilike(f"%{photographer}%")
        ).all()
    
    def get_by_quality_range(self, db: Session, min_quality: float = None, 
                           max_quality: float = None) -> List[InstallationPhoto]:
        """Get photos by quality score range"""
        query = db.query(InstallationPhoto)
        
        if min_quality is not None:
            query = query.filter(InstallationPhoto.quality_score >= min_quality)
        if max_quality is not None:
            query = query.filter(InstallationPhoto.quality_score <= max_quality)
        
        return query.all()


class ArtworkAppearanceCRUD(BaseCRUD):
    """CRUD operations for ArtworkAppearance model"""
    
    def __init__(self):
        super().__init__(ArtworkAppearance)
    
    def get_by_artwork(self, db: Session, artwork_id: str) -> List[ArtworkAppearance]:
        """Get all appearances of an artwork"""
        return db.query(ArtworkAppearance).filter(
            ArtworkAppearance.artwork_id == artwork_id
        ).all()
    
    def get_by_photo(self, db: Session, photo_id: str) -> List[ArtworkAppearance]:
        """Get all artwork appearances in a photo"""
        return db.query(ArtworkAppearance).filter(
            ArtworkAppearance.photo_id == photo_id
        ).all()
    
    def get_verified(self, db: Session) -> List[ArtworkAppearance]:
        """Get all verified appearances"""
        return db.query(ArtworkAppearance).filter(ArtworkAppearance.verified == True).all()
    
    def get_unverified(self, db: Session) -> List[ArtworkAppearance]:
        """Get all unverified appearances"""
        return db.query(ArtworkAppearance).filter(ArtworkAppearance.verified == False).all()
    
    def get_by_confidence_range(self, db: Session, min_confidence: float = None, 
                               max_confidence: float = None) -> List[ArtworkAppearance]:
        """Get appearances by confidence score range"""
        query = db.query(ArtworkAppearance)
        
        if min_confidence is not None:
            query = query.filter(ArtworkAppearance.matching_confidence >= min_confidence)
        if max_confidence is not None:
            query = query.filter(ArtworkAppearance.matching_confidence <= max_confidence)
        
        return query.all()
    
    def verify_appearance(self, db: Session, id: str, verified_by: str, 
                         notes: str = None) -> bool:
        """Verify an artwork appearance"""
        try:
            db_obj = self.get_by_id(db, id)
            if not db_obj:
                return False
            
            db_obj.verified = True
            db_obj.verified_by = verified_by
            db_obj.verification_date = datetime.now()
            if notes:
                db_obj.notes = notes
            
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error verifying appearance: {e}")
            db.rollback()
            raise
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Get statistics about artwork appearances"""
        total = db.query(ArtworkAppearance).count()
        verified = db.query(ArtworkAppearance).filter(ArtworkAppearance.verified == True).count()
        avg_confidence = db.query(func.avg(ArtworkAppearance.matching_confidence)).scalar() or 0
        
        return {
            "total_appearances": total,
            "verified_appearances": verified,
            "unverified_appearances": total - verified,
            "verification_rate": verified / total if total > 0 else 0,
            "average_confidence": float(avg_confidence)
        }