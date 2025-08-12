from domain_repository.operational.workflow import Workflow
from domain_repository.operational.component import Component
from domain_repository.operational.protocol import Protocol
from domain_repository.operational.expectation import Expectation


from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


ALLOWED_METADATA_TYPES: List = [
    "ComponentSchema",
    "ExpectationSchema",
    "ProtocolSchema",
    "WorkflowSchema",
]


class MetadataDocument(BaseModel):
    """
    Represents a JSON-LD metadata document with
    versioning, timestamps, soft-deprecation, and world-class ontology/semantic features.

    Attributes:
        id (UUID): Semantically meaningless unique identifier (UUID4).
        type (Literal): ["ComponentSchema", "ProtocolSchema", etc]
        context (Any): JSON-LD context (aliased as @context).
        version (int): Version number of the metadata document.
        created_at (datetime): UTC timestamp when document was created.
        updated_at (datetime): UTC timestamp when document was last updated.
        owner (Optional[str]): Owner of the metadata document.
        tags (Optional[List[str]]): Tags for filtering and categorization.
        data (Dict[str, Any]): Arbitrary JSON-LD payload.
        semantic_tags (Optional[List[str]]): Semantic tags or keywords (e.g., SKOS concepts).
        ontology_mappings (Optional[Dict[str, str]]): Mappings to external ontologies (e.g., skos:exactMatch, rdfs:subClassOf).
        external_references (Optional[List[str]]): URIs to external standards or documentation.
        constraints (Optional[List[Dict[str, Any]]]): SHACL-like or custom validation rules.
        parent_id (Optional[UUID]): Optional parent metamodel for explicit inheritance/subtyping.
        is_deprecated (bool): Whether metadata is deprecated (soft-deleted).
    """

    id: UUID = Field(
        default_factory=uuid4,
        description="Semantically meaningless unique identifier (UUID4)",
    )
    type: Literal["ComponentSchema", "ExpectationSchema", "ProtocolSchema", "WorkflowSchema"] = Field(
        ..., alias="@type", description="JSON-LD type (restricted)"
    )
    context: dict | str = Field(..., alias="@context", description="JSON-LD context.")
    version: int = Field(default=1, description="Version number")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the document was first created.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the document was last updated.",
    )
    owner: Optional[str] = Field(None, description="Owner of metadata")
    tags: Optional[List[str]] = Field(default_factory=list)

    data: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary JSON-LD payload."
    )
    semantic_tags: Optional[List[str]] = Field(default=None, description="Semantic tags or keywords (e.g., SKOS concepts)")
    ontology_mappings: Optional[Dict[str, str]] = Field(default=None, description="Mappings to external ontologies (e.g., skos:exactMatch, rdfs:subClassOf)")
    external_references: Optional[List[str]] = Field(default=None, description="URIs to external standards or documentation")
    constraints: Optional[List[Dict[str, Any]]] = Field(default=None, description="SHACL-like or custom validation rules")
    parent_id: Optional[UUID] = Field(default=None, description="Optional parent metamodel for explicit inheritance/subtyping")

    @model_validator(mode="after")
    def validate_data_size(self) -> "MetadataDocument":
        """
        Validate that the data field does
        not exceed max byte size when serialized to JSON.
        """
        import json

        data_bytes = len(json.dumps(self.data).encode("utf-8"))
        if data_bytes > 10_000:
            raise ValueError(f"data field exceeds maximum allowed size): {data_bytes}")
        return self

    is_deprecated: bool = Field(
        default=False, description="Whether this metadata is deprecated."
    )

    model_config = dict(
        validate_by_name=True,
        json_schema_extra={
            "example": {
                "@context": "https://schema.org/",
                "@type": "ComponentSchema",
                "data": {"input": {"type": "string"}},
                "tags": ["component", "v1"],
                "owner": "alice@example.com",
                "semantic_tags": ["acquisition", "data"],
                "ontology_mappings": {"skos:exactMatch": "https://schema.org/Action"},
                "external_references": ["https://schema.org/Action"],
                "constraints": [{"property": "input", "pattern": "^string$"}],
                "parent_id": None
            },
            "example_workflow": {
                "@context": "https://schema.org/",
                "@type": "WorkflowSchema",
                "data": {"name": "Test Workflow"},
                "tags": ["workflow", "v1"],
                "owner": "bob@example.com",
                "semantic_tags": ["pipeline", "etl"],
                "ontology_mappings": {"skos:exactMatch": "https://schema.org/Action"},
                "external_references": ["https://schema.org/Action"],
                "constraints": [{"property": "input", "pattern": "^string$"}],
                "parent_id": None
            }
        },
    )

    @model_validator(mode="before")
    @classmethod
    def ensure_jsonld_fields(cls, values: dict) -> dict:
        """
        Ensure that required JSON-LD fields (@context and @type) are present.

        Args:
            values (dict): The input values to validate.

        Returns:
            dict: The validated values.

        Raises:
            ValueError: If @context or @type is missing.
        """
        if "@context" not in values:
            raise ValueError("Missing required JSON-LD field: @context")
        if "@type" not in values:
            raise ValueError("Missing required JSON-LD field: @type")
        return values
