from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Body, Depends, status
from pydantic import BaseModel

from domain_repository.core.relationships import Relationship, RelationshipType
from domain_repository.core.registry import MetamodelRegistry

from .models import MetadataDocument
from .service import (
    get_metadata,
    register_metadata,
    update_metadata,
    deprecate_metadata,
    list_metadata,
    get_metadata_versions,
    MetadataRegistryError,
)

app = FastAPI(title="Metadata Registry Service")

# Dependency-injected registry for testability and flexibility
def get_registry():
    if not hasattr(app.state, "registry"):
        app.state.registry = MetamodelRegistry()
    return app.state.registry

# --- Auth and Rate Limiting Stubs ---
def require_auth():
    """Stub for authentication (replace with real logic)."""
    pass

def rate_limit():
    """Stub for rate limiting (replace with real logic)."""
    pass

# --- Relationship Endpoints ---
class RelationshipCreateRequest(BaseModel):
    source_id: UUID
    target_id: UUID
    relationship_type: RelationshipType
    metadata: Optional[dict] = None

@app.post(
    "/relationships",
    response_model=Relationship,
    status_code=201,
    tags=["Relationships"],
    description="Create a new relationship between entities."
)
def api_create_relationship(
    req: RelationshipCreateRequest,
    auth=Depends(require_auth),
    _=Depends(rate_limit),
    registry=Depends(get_registry),
) -> Relationship:
    """Create a new relationship between two entities."""
    # Explicitly check for entity existence before proceeding
    if not registry.entity_exists(req.source_id) or not registry.entity_exists(req.target_id):
        raise HTTPException(status_code=404, detail="Source or target entity not found.")
    try:
        rel = Relationship(
            source_id=req.source_id,
            target_id=req.target_id,
            relationship_type=req.relationship_type,
            metadata=req.metadata,
        )
        registry.relationship_manager.validate_relationship_constraints(rel, registry)
        registry.relationship_manager.add_relationship(rel)
        return rel
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get(
    "/relationships/{relationship_id}",
    response_model=Relationship,
    tags=["Relationships"],
    description="Get a specific relationship by its UUID."
)
def api_get_relationship(
    relationship_id: UUID,
    auth=Depends(require_auth),
    _=Depends(rate_limit),
    registry=Depends(get_registry),
) -> Relationship:
    """Get a specific relationship by its UUID."""
    mgr = registry.relationship_manager
    rel = mgr.relationships.get(relationship_id)
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found.")
    return rel

# --- Metadata Endpoints ---
@app.post(
    "/metadata",
    response_model=MetadataDocument,
    status_code=201,
    tags=["Metadata"],
    description="Register a new metadata document. Requires authentication.",
)
def api_register_metadata(
    doc: MetadataDocument,
    auth=Depends(require_auth),
    _=Depends(rate_limit),
) -> MetadataDocument:
    """Register a new metadata document."""
    try:
        return register_metadata(doc)
    except MetadataRegistryError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get(
    "/metadata/{metadata_id}",
    response_model=MetadataDocument,
    tags=["Metadata"],
    description="Retrieve a metadata document by its UUID.",
)
def api_get_metadata(
    metadata_id: UUID, auth=Depends(require_auth), _=Depends(rate_limit)
) -> MetadataDocument:
    """Retrieve a metadata document by its UUID."""
    try:
        return get_metadata(metadata_id)
    except MetadataRegistryError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put(
    "/metadata/{metadata_id}",
    response_model=MetadataDocument,
    tags=["Metadata"],
    description="Update an existing metadata document.",
)
def api_update_metadata(
    metadata_id: UUID,
    update: dict = Body(...),
    auth=Depends(require_auth),
    _=Depends(rate_limit),
) -> MetadataDocument:
    """Update an existing metadata document."""
    try:
        return update_metadata(metadata_id, update)
    except MetadataRegistryError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete(
    "/metadata/{metadata_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Metadata"],
    description="Deprecate (soft-delete) a metadata document.",
)
def api_deprecate_metadata(
    metadata_id: UUID, auth=Depends(require_auth), _=Depends(rate_limit)
) -> None:
    """Deprecate (soft-delete) a metadata document by its UUID."""
    try:
        deprecate_metadata(metadata_id)
    except MetadataRegistryError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return None

@app.get(
    "/metadata",
    response_model=List[MetadataDocument],
    tags=["Metadata"],
    description="List metadata documents.",
)
def api_list_metadata(
    type: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    include_deprecated: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    auth=Depends(require_auth),
    _=Depends(rate_limit),
) -> List[MetadataDocument]:
    """List metadata documents, optionally filtering by type, owner, tags, and deprecation status."""
    return list_metadata(
        type=type,
        owner=owner,
        tags=tags,
        include_deprecated=include_deprecated,
        limit=limit,
        offset=offset,
    )

@app.get("/metadata/{metadata_id}/versions", response_model=List[MetadataDocument])
def api_get_metadata_versions(metadata_id: UUID) -> List[MetadataDocument]:
    """Retrieve the version history for a metadata document."""
    return get_metadata_versions(metadata_id)


# --- List Relationships Endpoint ---
@app.get(
    "/relationships",
    response_model=List[Relationship],
    tags=["Relationships"],
    description="List all relationships in the registry."
)
def api_list_relationships(
    auth=Depends(require_auth),
    _=Depends(rate_limit),
    registry=Depends(get_registry),
) -> List[Relationship]:
    """List all relationships in the registry."""
    mgr = registry.relationship_manager
    return list(mgr.relationships.values())
