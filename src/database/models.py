from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()


class Artwork(Base):
    """
    Model for artwork metadata
    """
    __tablename__ = "artworks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    artist = Column(String(200), nullable=False)
    
    # Dimensions in centimeters
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    depth = Column(Float, nullable=True)
    
    # Medium and materials
    medium = Column(String(200), nullable=True)
    materials = Column(Text, nullable=True)
    
    # Artwork details
    creation_date = Column(String(50), nullable=True)  # Can be year, range, or "circa"
    description = Column(Text, nullable=True)
    provenance = Column(Text, nullable=True)
    
    # Cataloging information
    catalog_number = Column(String(100), nullable=True, unique=True)
    accession_number = Column(String(100), nullable=True)
    
    # Additional metadata
    style = Column(String(100), nullable=True)
    period = Column(String(100), nullable=True)
    subject_matter = Column(Text, nullable=True)
    
    # Digital assets
    reference_image_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)
    
    # Features for matching
    visual_features = Column(JSON, nullable=True)  # Stored embeddings/features
    color_palette = Column(JSON, nullable=True)    # Dominant colors
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    appearances = relationship("ArtworkAppearance", back_populates="artwork", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Artwork(id={self.id}, title='{self.title}', artist='{self.artist}')>"


class Exhibition(Base):
    """
    Model for exhibition records
    """
    __tablename__ = "exhibitions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(500), nullable=False)
    
    # Location details
    museum = Column(String(200), nullable=False)
    gallery = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Date range
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Exhibition details
    curator = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    type = Column(String(100), nullable=True)  # permanent, temporary, traveling
    
    # Additional metadata
    catalog_published = Column(Boolean, default=False)
    catalog_isbn = Column(String(20), nullable=True)
    website_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    photos = relationship("InstallationPhoto", back_populates="exhibition", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Exhibition(id={self.id}, name='{self.name}', museum='{self.museum}')>"


class InstallationPhoto(Base):
    """
    Model for installation/museum photos
    """
    __tablename__ = "installation_photos"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exhibition_id = Column(String, ForeignKey("exhibitions.id"), nullable=False)
    
    # File information
    image_path = Column(String(500), nullable=False)
    original_filename = Column(String(200), nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    
    # Image metadata
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    format = Column(String(10), nullable=True)  # jpg, png, etc.
    
    # Camera/capture information
    camera_make = Column(String(50), nullable=True)
    camera_model = Column(String(100), nullable=True)
    capture_date = Column(DateTime, nullable=True)
    photographer = Column(String(200), nullable=True)
    
    # Processing metadata
    processed = Column(Boolean, default=False)
    processing_date = Column(DateTime, nullable=True)
    detection_results = Column(JSON, nullable=True)  # Raw detection output
    
    # Location within museum
    room = Column(String(100), nullable=True)
    wall = Column(String(50), nullable=True)
    view_type = Column(String(50), nullable=True)  # overview, detail, angle
    
    # Additional metadata
    notes = Column(Text, nullable=True)
    quality_score = Column(Float, nullable=True)  # 0-1, image quality assessment
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    exhibition = relationship("Exhibition", back_populates="photos")
    artwork_appearances = relationship("ArtworkAppearance", back_populates="photo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<InstallationPhoto(id={self.id}, exhibition_id={self.exhibition_id}, path='{self.image_path}')>"


class ArtworkAppearance(Base):
    """
    Model for artwork appearances in installation photos
    """
    __tablename__ = "artwork_appearances"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artwork_id = Column(String, ForeignKey("artworks.id"), nullable=False)
    photo_id = Column(String, ForeignKey("installation_photos.id"), nullable=False)
    
    # Bounding box coordinates (normalized 0-1)
    bbox_x = Column(Float, nullable=False)
    bbox_y = Column(Float, nullable=False)
    bbox_width = Column(Float, nullable=False)
    bbox_height = Column(Float, nullable=False)
    
    # Detection confidence and matching score
    detection_confidence = Column(Float, nullable=False)  # 0-1, from object detection
    matching_confidence = Column(Float, nullable=False)   # 0-1, from feature matching
    
    # Verification status
    verified = Column(Boolean, default=False)
    verified_by = Column(String(100), nullable=True)
    verification_date = Column(DateTime, nullable=True)
    
    # Visual context
    cropped_image_path = Column(String(500), nullable=True)
    features = Column(JSON, nullable=True)  # Extracted features for this appearance
    
    # Metadata
    visible_percentage = Column(Float, nullable=True)  # How much of artwork is visible
    occlusion_level = Column(String(20), nullable=True)  # none, partial, heavy
    lighting_quality = Column(String(20), nullable=True)  # good, moderate, poor
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    artwork = relationship("Artwork", back_populates="appearances")
    photo = relationship("InstallationPhoto", back_populates="artwork_appearances")
    
    def __repr__(self):
        return f"<ArtworkAppearance(id={self.id}, artwork_id={self.artwork_id}, photo_id={self.photo_id}, confidence={self.matching_confidence})>"