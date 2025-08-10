from typing import Dict, List, Optional
from uuid import UUID
from copy import deepcopy
import logging
from .models import MetadataDocument
from datetime import datetime, timezone


# In-memory store for demonstration (replace with DB in production)
_metadata_store: Dict[UUID, MetadataDocument] = {}
_metadata_versions: Dict[UUID, List[MetadataDocument]] = {}

# Configure logging
logger = logging.getLogger("metadata_registry_svc")
logging.basicConfig(level=logging.INFO)


# Custom exception for domain errors
class MetadataRegistryError(Exception):
    pass


def register_metadata(doc: MetadataDocument) -> MetadataDocument:
    """
    Register a new metadata document.

    Args:
        doc (MetadataDocument): The metadata document to register.

    Returns:
        MetadataDocument: The registered metadata document.

    Raises:
        ValueError: If a document with the same ID already exists.
    """
    if doc.id in _metadata_store:
        logger.warning(f"Attempt to register duplicate metadata ID: {doc.id}")
        raise MetadataRegistryError("Metadata with this ID already exists.")
    _metadata_store[doc.id] = doc
    _metadata_versions[doc.id] = [deepcopy(doc)]
    logger.info(f"Registered metadata: {doc.id}")
    return doc


def get_metadata(metadata_id: UUID) -> MetadataDocument:
    """
    Retrieve a metadata document by its UUID.

    Args:
        metadata_id (UUID): The UUID of the metadata document.

    Returns:
        MetadataDocument: The found metadata document.

    Raises:
        KeyError: If the document is not found.
    """
    doc = _metadata_store.get(metadata_id)
    if not doc:
        logger.warning(f"Metadata not found: {metadata_id}")
        raise MetadataRegistryError("Metadata not found.")
    return doc


def update_metadata(metadata_id: UUID, update: dict) -> MetadataDocument:
    """
    Update an existing metadata document,
    incrementing its version and updating the timestamp.

    Args:
        metadata_id (UUID): The UUID of the metadata document to update.
        update (dict): The fields to update in the metadata document.

    Returns:
        MetadataDocument: The updated metadata document.

    Raises:
        KeyError: If the document is not found.
        ValueError: If the document is deprecated and cannot be updated.
    """
    doc = get_metadata(metadata_id)
    if doc.is_deprecated:
        logger.warning(f"Attempt to update deprecated metadata: {metadata_id}")
        raise MetadataRegistryError("Cannot update deprecated metadata.")
    # Prevent updates to immutable fields
    immutable_fields = {"id", "created_at"}
    for key in update:
        if key in immutable_fields:
            logger.error(f"Attempt to update immutable field '{key}' in: {metadata_id}")
            raise MetadataRegistryError(f"Can't update immutable field: {key}")
    # Always preserve the original created_at
    update_with_created = {
        **update,
        "created_at": doc.created_at,
        "updated_at": datetime.now(timezone.utc),
    }
    updated_doc = doc.model_copy(update=update_with_created, deep=True)
    updated_doc.version += 1
    _metadata_store[metadata_id] = updated_doc
    _metadata_versions[metadata_id].append(deepcopy(updated_doc))
    logger.info(f"Updated: {metadata_id} (version {updated_doc.version})")
    return updated_doc


def deprecate_metadata(metadata_id: UUID) -> MetadataDocument:
    """
    Deprecate (soft-delete) a metadata document by setting
    its is_deprecated flag.

    Args:
        metadata_id (UUID): The UUID of the metadata document to deprecate.

    Returns:
        MetadataDocument: The deprecated metadata document.

    Raises:
        KeyError: If the document is not found.
    """
    doc = get_metadata(metadata_id)
    if doc.is_deprecated:
        logger.info(f"Deprecate called on eprecated metadata: {metadata_id}")
        return doc
    # Always preserve the original created_at
    update_with_created = {
        "is_deprecated": True,
        "created_at": doc.created_at,
        "updated_at": datetime.now(timezone.utc),
    }
    updated_doc = doc.model_copy(update=update_with_created, deep=True)
    _metadata_store[metadata_id] = updated_doc
    _metadata_versions[metadata_id].append(deepcopy(updated_doc))
    logger.info(f"Deprecated metadata: {metadata_id}")
    return updated_doc


def list_metadata(
    type: Optional[str] = None,
    owner: Optional[str] = None,
    tags: Optional[List[str]] = None,
    include_deprecated: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> List[MetadataDocument]:
    """
    List metadata documents, optionally filtering by
    type, owner, tags, and deprecation status.
    Supports pagination.

    Args:
        type (Optional[str]): Filter by metadata type (JSON-LD @type).
        owner (Optional[str]): Filter by owner.
        tags (Optional[List[str]]): Filter by tags (all tags must be present).
        include_deprecated (bool): Whether to include deprecated documents.
        limit (int): Maximum number of results to return.
        offset (int): Number of results to skip (for pagination).

    Returns:
        List[MetadataDocument]: List of matching metadata documents.
    """
    results = list(_metadata_store.values())
    if not include_deprecated:
        results = [d for d in results if not d.is_deprecated]
    if type:
        results = [d for d in results if d.type == type]
    if owner:
        results = [d for d in results if d.owner == owner]
    if tags:
        results = [d for d in results if set(tags).issubset(set(d.tags or []))]
    paginated = results[offset : offset + limit]
    logger.info(f"Metadata: {len(paginated)}, (offset={offset}, limit={limit})")
    return paginated


def get_metadata_versions(metadata_id: UUID) -> List[MetadataDocument]:
    """
    Retrieve the version history for a metadata document.

    Args:
        metadata_id (UUID): The UUID of the metadata document.

    Returns:
        List[MetadataDocument]: List of all versions of the metadata document.
    """
    versions = _metadata_versions.get(metadata_id)
    if not versions:
        logger.warning(f"Metadata versions not found: {metadata_id}")
        raise MetadataRegistryError("Metadata versions not found.")
    return versions
