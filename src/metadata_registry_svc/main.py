from uuid import UUID
from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException, Query, Body, Depends, status
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


# --- Auth and Rate Limiting Stubs ---
def require_auth():
    # Replace with real authentication logic
    pass


def rate_limit():
    # Replace with real rate limiting logic
    pass


@app.post(
    "/metadata",
    response_model=MetadataDocument,
    status_code=201,
    tags=["Metadata"],
    description="Register a new metadata document. Requires authentication.",
)
def api_register_metadata(
    doc: MetadataDocument,
    auth: Any = Depends(require_auth),
    _: Any = Depends(rate_limit),
) -> MetadataDocument:
    """
    Register a new metadata document.

    Args:
        doc (MetadataDocument): The metadata document to register.

    Returns:
        MetadataDocument: The registered metadata document.

    Raises:
        HTTPException: If a document with the same ID already exists.
    """
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
    metadata_id: UUID, auth: Any = Depends(require_auth), _: Any = Depends(rate_limit)
) -> MetadataDocument:
    """
    Retrieve a metadata document by its UUID.

    Args:
        metadata_id (UUID): The UUID of the metadata document.

    Returns:
        MetadataDocument: The found metadata document.

    Raises:
        HTTPException: If the document is not found.
    """
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
    auth: Any = Depends(require_auth),
    _: Any = Depends(rate_limit),
) -> MetadataDocument:
    """
    Update an existing metadata document.

    Args:
        metadata_id (UUID): The UUID of the metadata document to update.
        update (dict): The fields to update in the metadata document.

    Returns:
        MetadataDocument: The updated metadata document.

    Raises:
        HTTPException: If the document is not found or is deprecated.
    """
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
    metadata_id: UUID, auth: Any = Depends(require_auth), _: Any = Depends(rate_limit)
) -> None:
    """
    Deprecate (soft-delete) a metadata document by its UUID.

    Args:
        metadata_id (UUID): The UUID of the metadata document to deprecate.

    Returns:
        MetadataDocument: The deprecated metadata document.

    Raises:
        HTTPException: If the document is not found.
    """
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
    auth: Any = Depends(require_auth),
    _: Any = Depends(rate_limit),
) -> List[MetadataDocument]:
    """
    List metadata documents, optionally filtering by
    type, owner, tags, and deprecation status. Supports pagination.
    """
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
    """
    Retrieve the version history for a metadata document.

    Args:
        metadata_id (UUID): The UUID of the metadata document.

    Returns:
        List[MetadataDocument]: List of all versions of the metadata document.
    """
    return get_metadata_versions(metadata_id)
