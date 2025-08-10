# metadata-registry-svc

A world-class, extensible service for registering, validating, and discovering metadata schemas and semantic mappings (e.g., JSON-LD) for a distributed, event-driven platform.

## Features
- CRUD for metadata schemas
- Validation endpoint
- Discovery/listing endpoint
- OpenAPI docs
- Built with FastAPI and Pydantic

## Quickstart
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.metadata_registry_svc.main:app --reload
```
