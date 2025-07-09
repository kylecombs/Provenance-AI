# PostgreSQL Cloud Setup Guide

This guide provides instructions for setting up cloud PostgreSQL instances for production deployment.

## AWS RDS PostgreSQL

### 1. Create RDS Instance

```bash
# Using AWS CLI
aws rds create-db-instance \
    --db-instance-identifier artwork-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username artwork_admin \
    --master-user-password YOUR_SECURE_PASSWORD \
    --allocated-storage 20 \
    --storage-type gp2 \
    --db-name artwork_db \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --publicly-accessible \
    --multi-az \
    --backup-retention-period 7
```

### 2. Connection String
```bash
DATABASE_URL=postgresql://artwork_admin:PASSWORD@artwork-db.cluster-xyz.us-east-1.rds.amazonaws.com:5432/artwork_db
```

### 3. Security Groups
```bash
# Allow inbound PostgreSQL traffic
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 5432 \
    --source-group sg-yyyyyyyyy
```

## Google Cloud SQL

### 1. Create Cloud SQL Instance

```bash
# Using gcloud CLI
gcloud sql instances create artwork-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-size=20GB \
    --storage-type=SSD \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04
```

### 2. Create Database and User

```bash
# Create database
gcloud sql databases create artwork_db --instance=artwork-db

# Create user
gcloud sql users create artwork_user \
    --instance=artwork-db \
    --password=YOUR_SECURE_PASSWORD
```

### 3. Connection String
```bash
DATABASE_URL=postgresql://artwork_user:PASSWORD@INSTANCE_IP:5432/artwork_db
```

## Azure Database for PostgreSQL

### 1. Create Azure Database

```bash
# Using Azure CLI
az postgres server create \
    --resource-group artwork-rg \
    --name artwork-db \
    --location eastus \
    --admin-user artwork_admin \
    --admin-password YOUR_SECURE_PASSWORD \
    --sku-name B_Gen5_1 \
    --version 14
```

### 2. Configure Firewall

```bash
# Allow Azure services
az postgres server firewall-rule create \
    --resource-group artwork-rg \
    --server artwork-db \
    --name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Allow specific IP
az postgres server firewall-rule create \
    --resource-group artwork-rg \
    --server artwork-db \
    --name AllowMyIP \
    --start-ip-address YOUR_IP \
    --end-ip-address YOUR_IP
```

### 3. Connection String
```bash
DATABASE_URL=postgresql://artwork_admin@artwork-db:PASSWORD@artwork-db.postgres.database.azure.com:5432/postgres
```

## Heroku Postgres

### 1. Add Heroku Postgres Add-on

```bash
# For existing Heroku app
heroku addons:create heroku-postgresql:hobby-dev

# Get database URL
heroku config:get DATABASE_URL
```

### 2. Connection String
```bash
# Heroku automatically sets DATABASE_URL
DATABASE_URL=postgres://username:password@hostname:5432/database_name
```

## DigitalOcean Managed Database

### 1. Create Database Cluster

```bash
# Using doctl CLI
doctl databases create artwork-db \
    --engine postgres \
    --version 14 \
    --size db-s-1vcpu-1gb \
    --region nyc3 \
    --num-nodes 1
```

### 2. Connection String
```bash
DATABASE_URL=postgresql://doadmin:PASSWORD@artwork-db-do-user-123456-0.db.ondigitalocean.com:25060/defaultdb?sslmode=require
```

## SSL/TLS Configuration

Most cloud providers require SSL connections. Update your configuration:

```python
# In config.py
import ssl

# For production with SSL
if os.getenv("ENVIRONMENT") == "production":
    DATABASE_CONFIG["ssl_context"] = ssl.create_default_context()
    DATABASE_CONFIG["ssl_context"].check_hostname = False
    DATABASE_CONFIG["ssl_context"].verify_mode = ssl.CERT_NONE
```

## Environment Variables

Set these environment variables for production:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Application
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

## Migration Commands

```bash
# Run migrations on production database
alembic upgrade head

# Check current migration version
alembic current

# Create new migration
alembic revision --autogenerate -m "Add new feature"
```

## Monitoring and Maintenance

### 1. Database Monitoring

```python
# Add to your application
from src.database import get_db_info

# Monitor connection pool
def check_database_health():
    db_info = get_db_info()
    return {
        "database": db_info.get("version"),
        "pool_size": db_info.get("pool_size"),
        "checked_out": db_info.get("checked_out")
    }
```

### 2. Backup Strategy

```bash
# Manual backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL | gzip > backup_${DATE}.sql.gz
aws s3 cp backup_${DATE}.sql.gz s3://artwork-backups/
```

### 3. Performance Tuning

```sql
-- Check slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, seq_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## Security Best Practices

1. **Use strong passwords** with at least 16 characters
2. **Enable SSL/TLS** for all connections
3. **Restrict network access** to specific IP ranges
4. **Regular security updates** for database software
5. **Monitor access logs** for suspicious activity
6. **Use environment variables** for sensitive configuration
7. **Regular backups** with encryption at rest

## Cost Optimization

### 1. Right-sizing Instances

```bash
# Start small and scale up
# Development: db.t3.micro (AWS) or db-f1-micro (GCP)
# Production: db.t3.small or larger based on load
```

### 2. Storage Optimization

```bash
# Use GP2 storage for development
# Use GP3 or Provisioned IOPS for production
# Monitor storage usage and adjust as needed
```

### 3. Connection Pooling

```python
# Configure connection pooling
DATABASE_CONFIG = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_pre_ping": True,
    "pool_recycle": 3600  # 1 hour
}
```

## Troubleshooting

### Connection Issues

```bash
# Test connection
psql $DATABASE_URL -c "SELECT version();"

# Check firewall rules
telnet hostname 5432

# Verify SSL requirements
psql $DATABASE_URL -c "SHOW ssl;"
```

### Performance Issues

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

### Migration Issues

```bash
# Check current schema
alembic current

# Show migration history
alembic history

# Rollback problematic migration
alembic downgrade <previous_revision>
```