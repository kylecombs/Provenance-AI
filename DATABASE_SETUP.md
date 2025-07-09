# Database Setup Guide

This guide explains how to set up and configure the database for the artwork identifier application.

## Database Schema

The application uses four main tables:

### 1. Artworks
- **id**: Primary key (UUID)
- **title**: Artwork title
- **artist**: Artist name
- **dimensions**: Width, height, depth in cm
- **medium**: Art medium/materials
- **creation_date**: When artwork was created
- **catalog_number**: Unique catalog identifier
- **reference_image_path**: Path to reference image
- **visual_features**: Stored embeddings for matching
- **color_palette**: Dominant colors (JSON)

### 2. Exhibitions
- **id**: Primary key (UUID)
- **name**: Exhibition name
- **museum**: Museum/gallery name
- **location**: City, country
- **date_range**: Start and end dates
- **curator**: Exhibition curator
- **type**: permanent, temporary, traveling

### 3. Installation Photos
- **id**: Primary key (UUID)
- **exhibition_id**: Foreign key to exhibitions
- **image_path**: Path to photo file
- **metadata**: Camera info, capture date, photographer
- **processing_info**: Detection results, processing status
- **quality_score**: Image quality assessment (0-1)

### 4. Artwork Appearances
- **id**: Primary key (UUID)
- **artwork_id**: Foreign key to artworks
- **photo_id**: Foreign key to installation_photos
- **bounding_box**: Normalized coordinates (x, y, width, height)
- **confidence_scores**: Detection and matching confidence
- **verification_status**: Manual verification info
- **visual_context**: Occlusion, lighting, visibility

## Database Configuration

### SQLite (Development)
Default configuration uses SQLite for development:
```python
DATABASE_URL = "sqlite:///artwork_db.sqlite"
```

### PostgreSQL (Production)
For production, configure PostgreSQL:

1. **Install PostgreSQL**
```bash
# macOS with Homebrew
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
```

2. **Create Database and User**
```sql
-- Connect as postgres user
sudo -u postgres psql

-- Create database
CREATE DATABASE artwork_db;

-- Create user
CREATE USER artwork_user WITH PASSWORD 'your_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE artwork_db TO artwork_user;
```

3. **Configure Environment Variables**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
DATABASE_URL=postgresql://artwork_user:your_password@localhost:5432/artwork_db
```

### Cloud PostgreSQL
For cloud deployment, use managed PostgreSQL services:

- **AWS RDS**: Amazon Relational Database Service
- **Google Cloud SQL**: Google's managed PostgreSQL
- **Azure Database**: Microsoft's managed PostgreSQL
- **Heroku Postgres**: Heroku's managed PostgreSQL

Example cloud configuration:
```bash
DATABASE_URL=postgresql://username:password@host:5432/database
```

## Database Setup Commands

### 1. Initialize Database
```bash
# Activate virtual environment
source artwork-identifier-env/bin/activate

# Test database connection
python database_setup.py --test

# Initialize database tables
python database_setup.py --setup
```

### 2. Run Database Migrations
```bash
# Create migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# View migration history
alembic history

# Rollback to previous version
alembic downgrade -1
```

### 3. Create Sample Data
```bash
# Create sample data for testing
python database_setup.py --sample-data

# Test CRUD operations
python database_setup.py --test-crud

# Run all setup operations
python database_setup.py --all
```

## Database Management

### Backup and Restore

#### SQLite
```bash
# Backup
cp artwork_db.sqlite artwork_db_backup.sqlite

# Restore
cp artwork_db_backup.sqlite artwork_db.sqlite
```

#### PostgreSQL
```bash
# Backup
pg_dump artwork_db > artwork_db_backup.sql

# Restore
psql artwork_db < artwork_db_backup.sql
```

### Performance Optimization

#### Indexes
The schema includes indexes on commonly queried fields:
- artwork.catalog_number (unique)
- artwork.artist
- artwork.title
- exhibition.name
- exhibition.museum
- installation_photos.exhibition_id
- artwork_appearances.artwork_id
- artwork_appearances.photo_id

#### Query Optimization
- Use specific filters to reduce result sets
- Leverage database statistics for query planning
- Monitor slow queries and optimize as needed

## CRUD Operations

### Python API Usage

```python
from src.database import get_db
from src.database import ArtworkCRUD, ExhibitionCRUD

# Get database session
with get_db() as db:
    artwork_crud = ArtworkCRUD()
    
    # Create artwork
    artwork = artwork_crud.create(
        db=db,
        title="The Starry Night",
        artist="Vincent van Gogh",
        medium="Oil on canvas"
    )
    
    # Search by artist
    van_gogh_works = artwork_crud.search_by_artist(db, "Van Gogh")
    
    # Get by catalog number
    artwork = artwork_crud.get_by_catalog_number(db, "MoMA-472.1941")
    
    # Update artwork
    updated = artwork_crud.update(
        db=db,
        id=artwork.id,
        description="Updated description"
    )
```

### Database Queries

```python
# Complex queries with joins
from src.database.models import Artwork, Exhibition, ArtworkAppearance

# Get artworks with their appearances
artworks_with_appearances = db.query(Artwork).join(
    ArtworkAppearance
).filter(
    ArtworkAppearance.matching_confidence > 0.8
).all()

# Get exhibitions with photo counts
exhibitions_with_counts = db.query(
    Exhibition.name,
    func.count(InstallationPhoto.id).label('photo_count')
).join(InstallationPhoto).group_by(Exhibition.id).all()
```

## Testing

### Unit Tests
```bash
# Run database tests
python -m pytest tests/test_database.py

# Run with coverage
python -m pytest tests/test_database.py --cov=src.database
```

### Integration Tests
```bash
# Test full workflow
python database_setup.py --all
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check database server is running
   - Verify credentials in .env file
   - Check firewall settings

2. **Migration Errors**
   - Ensure database is accessible
   - Check for conflicting schema changes
   - Review migration files for syntax errors

3. **Performance Issues**
   - Add indexes for frequently queried fields
   - Optimize query patterns
   - Consider connection pooling

### Debug Mode
```python
# Enable SQL logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## Security Considerations

- Never commit database credentials to version control
- Use environment variables for sensitive configuration
- Implement proper access controls
- Regular security updates for database software
- Enable SSL/TLS for database connections in production
- Regular backups and disaster recovery planning