# RAGFlow Integration Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the RAGFlow integration with Compliant.One platform.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.10+ environment
- At least 8GB RAM available for RAGFlow services
- Network access for downloading Docker images

## 1. Environment Setup

### 1.1 Create Environment Variables

Create a `.env` file in the project root:

```bash
# RAGFlow Configuration
RAGFLOW_API_URL=http://localhost:9380
RAGFLOW_API_KEY=your_api_key_here
RAGFLOW_ADMIN_USER=admin
RAGFLOW_ADMIN_PASSWORD=admin_password

# OpenAI Configuration (optional)
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=your_anthropic_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Database Configuration
MYSQL_PASSWORD=infini_rag_flow
MINIO_USER=ROOTUSER
MINIO_PASSWORD=CHANGEME123

# Redis Configuration
REDIS_PASSWORD=infini_rag_flow

# Performance Settings
RAGFLOW_MAX_WORKERS=4
RAGFLOW_CHUNK_SIZE=1024
RAGFLOW_TIMEOUT=300
```

### 1.2 Set File Permissions

```bash
chmod 600 .env
```

## 2. RAGFlow Service Deployment

### 2.1 Deploy RAGFlow with Docker Compose

Use the provided docker-compose configuration:

```bash
# Navigate to RAGFlow integration directory
cd /root/compliant-one/integrations/ragflow

# Start RAGFlow services
docker-compose up -d
```

### 2.2 Verify Services are Running

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f

# Verify API health
curl http://localhost:9380/v1/health
```

Expected services:
- `ragflow-mysql`: MySQL database
- `ragflow-redis`: Redis cache
- `ragflow-minio`: MinIO object storage
- `ragflow-es01`: Elasticsearch
- `ragflow-api`: RAGFlow API server

### 2.3 Initialize RAGFlow

```bash
# Wait for all services to be healthy (may take 2-3 minutes)
docker-compose exec ragflow-api curl -f http://localhost:9380/v1/health

# Initialize default knowledge base
python -c "
import asyncio
from integrations.ragflow import RAGFlowIntegration

async def init():
    integration = RAGFlowIntegration()
    await integration.initialize()
    print('RAGFlow integration initialized successfully')
    await integration.cleanup()

asyncio.run(init())
"
```

## 3. Compliant.One Configuration

### 3.1 Install Python Dependencies

```bash
# Install additional dependencies for RAGFlow integration
pip install -r requirements.txt
```

### 3.2 Update Configuration

Edit `config/settings.py` to include RAGFlow settings:

```python
# Add to existing settings
RAGFLOW_ENABLED = True
RAGFLOW_API_URL = os.getenv("RAGFLOW_API_URL", "http://localhost:9380")
RAGFLOW_API_KEY = os.getenv("RAGFLOW_API_KEY")

# AI Model Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

## 4. Testing the Integration

### 4.1 Basic Health Check

```python
import asyncio
from services.ai.ragflow_client import RAGFlowClient

async def test_connection():
    client = RAGFlowClient()
    health = await client.get_health()
    print(f"RAGFlow Health: {health}")
    await client.close()

asyncio.run(test_connection())
```

### 4.2 Document Upload Test

```python
import asyncio
from integrations.ragflow import RAGFlowIntegration

async def test_upload():
    integration = RAGFlowIntegration()
    await integration.initialize()
    
    # Test document upload
    result = await integration.upload_document(
        file_path="test_document.pdf",
        document_type="aml_policy"
    )
    print(f"Upload result: {result}")
    
    await integration.cleanup()

asyncio.run(test_upload())
```

### 4.3 Search Test

```python
import asyncio
from integrations.ragflow import RAGFlowIntegration

async def test_search():
    integration = RAGFlowIntegration()
    await integration.initialize()
    
    # Test search functionality
    results = await integration.search_documents(
        query="AML policy requirements",
        limit=5
    )
    print(f"Search results: {len(results)} documents found")
    
    await integration.cleanup()

asyncio.run(test_search())
```

## 5. Dashboard Access

### 5.1 Launch Streamlit Dashboard

```bash
# Start the main dashboard
streamlit run dashboard/main.py --server.port 8502

# Or start the AI compliance dashboard specifically
streamlit run dashboard/ai_compliance.py --server.port 8503
```

### 5.2 Access AI Compliance Features

Navigate to: `http://localhost:8503`

Available features:
- **Document Upload**: Single and batch document processing
- **Smart Search**: Semantic search across compliance documents
- **AI Chat**: Compliance Q&A and guidance
- **Analytics**: Document processing metrics and insights
- **Settings**: Configuration management

## 6. Production Deployment

### 6.1 Security Hardening

```bash
# Generate secure API keys
export RAGFLOW_API_KEY=$(openssl rand -hex 32)

# Use secure passwords
export MYSQL_PASSWORD=$(openssl rand -hex 16)
export REDIS_PASSWORD=$(openssl rand -hex 16)
export MINIO_PASSWORD=$(openssl rand -hex 16)
```

### 6.2 Resource Allocation

Recommended resources for production:

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  ragflow-api:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
  
  ragflow-es01:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1'
    environment:
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
```

### 6.3 Monitoring Setup

```bash
# Enable logging
export RAGFLOW_LOG_LEVEL=INFO

# Set up log rotation
echo "*/5 * * * * docker system prune -f" | crontab -
```

## 7. Backup and Maintenance

### 7.1 Database Backup

```bash
# Backup MySQL data
docker-compose exec ragflow-mysql mysqldump -u root -p$MYSQL_PASSWORD rag > backup_$(date +%Y%m%d).sql

# Backup MinIO data
docker-compose exec ragflow-minio mc mirror /data /backup/minio_$(date +%Y%m%d)
```

### 7.2 Update Services

```bash
# Pull latest images
docker-compose pull

# Restart with new images
docker-compose down && docker-compose up -d
```

## 8. Troubleshooting

### 8.1 Common Issues

**Service won't start:**
```bash
# Check logs
docker-compose logs ragflow-api

# Restart specific service
docker-compose restart ragflow-api
```

**Connection timeout:**
```bash
# Increase timeout in .env
RAGFLOW_TIMEOUT=600

# Restart services
docker-compose restart
```

**Out of memory:**
```bash
# Check resource usage
docker stats

# Increase memory limits in docker-compose.yml
```

### 8.2 Performance Tuning

```bash
# Optimize Elasticsearch
curl -X PUT "localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "persistent": {
    "indices.memory.index_buffer_size": "20%"
  }
}'

# Adjust worker count
export RAGFLOW_MAX_WORKERS=8
```

## 9. Health Monitoring

### 9.1 Health Check Endpoints

```bash
# RAGFlow API health
curl http://localhost:9380/v1/health

# Elasticsearch health
curl http://localhost:9200/_cluster/health

# MinIO health
curl http://localhost:9001/minio/health/live
```

### 9.2 Automated Monitoring

Create a monitoring script:

```bash
#!/bin/bash
# monitor_ragflow.sh

services=("ragflow-api" "ragflow-mysql" "ragflow-redis" "ragflow-minio" "ragflow-es01")

for service in "${services[@]}"; do
    if ! docker-compose ps $service | grep -q "Up"; then
        echo "ALERT: $service is down"
        docker-compose restart $service
    fi
done
```

## Support

For issues specific to RAGFlow integration:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables are set correctly
3. Ensure all services are healthy
4. Review the integration documentation in `RAGFLOW_INTEGRATION_PLAN.md`

For general platform support, refer to the main Compliant.One documentation.
