# Quickstart

1. **Run the API locally:**
	```sh
	uvicorn src.metadata_registry_svc.main:app --reload
	```
	The API will be available at http://127.0.0.1:8000

2. **Explore the API:**
	- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
	- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

3. **Try a request:**
	```sh
	curl -X GET http://127.0.0.1:8000/metadata
	```

---

# Schemas

## MetadataDocument
```json
{
	"id": "UUID",
	"@type": "ComponentSchema | ExpectationSchema | ProtocolSchema | WorkflowSchema",
	"@context": "object | string",
	"version": 1,
	"created_at": "datetime",
	"updated_at": "datetime",
	"owner": "string | null",
	"tags": ["string", ...],
	"data": {"any": "object"},
	"semantic_tags": ["string", ...],
	"ontology_mappings": {"string": "string"},
	"external_references": ["string", ...],
	"constraints": [{"any": "object"}],
	"parent_id": "UUID | null",
	"is_deprecated": false
}
```

## Relationship
```json
{
	"id": "UUID",
	"source_id": "UUID",
	"target_id": "UUID",
	"relationship_type": "contains | implements | expects | depends_on | composed_of | extends",
	"metadata": {"any": "object"}
}
```

## RelationshipCreateRequest
```json
{
	"source_id": "UUID",
	"target_id": "UUID",
	"relationship_type": "contains | implements | expects | depends_on | composed_of | extends",
	"metadata": {"any": "object"}
}
```

---
# FAQ & Troubleshooting

**Q: Why do I get a 404 or 400 error when creating a relationship?**
A: Ensure both source and target UUIDs exist and the relationship type is valid for those entity types.

**Q: How do I authenticate?**
A: Authentication is stubbed in development. In production, use the `Authorization` header with a bearer token or API key.

**Q: How do I see all available endpoints and schemas?**
A: Visit `/docs` or `/redoc` on your running API for interactive documentation.

**Q: What is the format for UUIDs?**
A: All UUIDs must be RFC 4122-compliant (e.g., `123e4567-e89b-12d3-a456-426614174000`).

**Q: How do I report a bug or request a feature?**
A: Open an issue in the repository or contact the maintainers listed in the README.

---
# Notes

- All UUIDs must be valid and refer to existing entities.
- Relationship types are validated for semantic correctness.
- All responses are JSON; errors follow standard HTTP error codes and messages.
- For a visual model, see the architecture diagrams in the main README.

---

# Metadata Registry Service API Reference

This document provides a comprehensive overview of the REST API for the Metadata Registry Service, now supporting polymorphic metamodels and type-safe relationships.
All endpoints are JSON-based and follow RESTful conventions. Authentication and rate limiting are stubbed for future implementation.

## Base URL

```
https://<your-domain>/
```

## Endpoints

### Register Metadata (Polymorphic)

**POST** `/metadata`

Registers a new metadata document (workflow, component, expectation, protocol, etc.) using the polymorphic registry.


**Request Body Example (with ontology/semantic features, relationship-centric):**
```json
{
	"@type": "ComponentSchema",
	"@context": {"@vocab": "http://example.com/"},
	"data": {
		"name": "Acquisition"
	},
	"owner": "alice",
	"tags": ["tag1", "tag2"],
	"semantic_tags": ["acquisition", "data"],
	"ontology_mappings": {"skos:broader": "https://schema.org/Action"},
	"external_references": ["https://schema.org/Action"],
	"constraints": [],
	"parent_id": null
}
```

**Response Example (with ontology/semantic features, relationship-centric):**
```json
{
	"id": "<uuid>",
	"@type": "ComponentSchema",
	"@context": {"@vocab": "http://example.com/"},
	"data": {
		"name": "Acquisition"
	},
	"owner": "alice",
	"tags": ["tag1", "tag2"],
	"semantic_tags": ["acquisition", "data"],
	"ontology_mappings": {"skos:broader": "https://schema.org/Action"},
	"external_references": ["https://schema.org/Action"],
	"constraints": [],
	"parent_id": null
}
```
	"created_at": "2025-08-10T12:00:00Z",
	"updated_at": "2025-08-10T12:00:00Z",
	"is_deprecated": false
}
```

---

### Register Relationship (Explicit)

**POST** `/relationships`

Registers an explicit relationship between two metamodels (e.g., workflow contains component, component implements protocol, etc.).

**Request Body Example:**
```json
{
	"source_id": "<workflow-uuid>",
	"target_id": "<component-uuid>",
	"relationship_type": "contains",
	"metadata": {"added_via": "service"}
}
```

**Response Example:**
```json
{
	"id": "<relationship-uuid>",
	"source_id": "<workflow-uuid>",
	"target_id": "<component-uuid>",
	"relationship_type": "contains",
	"metadata": {"added_via": "service"}
}
```
---
## Best Practices & Migration Note
- All entity connections are managed via explicit Relationship objects—never direct fields.
- Ontology/semantic fields and provenance are present and first-class.
- SHACL/OWL constraints are supported for advanced validation.
- All JSON-LD and API payloads reflect the decoupled, relationship-centric model.
- If upgrading from a previous version, remove all direct reference fields (e.g., `component_ids`, `protocol_id`, `expectation_id`) from your code and use explicit relationships instead.

## Validation Checklist (World-Class Ontology Review)
- [x] All entity connections are explicit relationships
- [x] Ontology/semantic fields and provenance are present
- [x] SHACL/OWL constraints supported
- [x] JSON-LD serialization for all entities and relationships
- [x] Registry and relationship manager are central to all operations

---

### Get Metadata by ID

**GET** `/metadata/{metadata_id}`

Retrieves a metadata document by its UUID.

**Response Example:**
```json
{
	"id": "<uuid>",
	"@type": "ComponentSchema",
	"@context": {"@vocab": "http://example.com/"},
	"data": { ... }
}
```

---

### List Metadata

**GET** `/metadata`

Lists metadata documents. Supports filtering by type, owner, tags, and pagination.

**Query Parameters:**
- `type` (optional): Filter by metadata type
- `owner` (optional): Filter by owner
- `tags` (optional, comma-separated): Filter by tags
- `include_deprecated` (optional, bool): Include deprecated documents
- `limit` (optional, int): Max results (default 50)
- `offset` (optional, int): Pagination offset

**Response Example:**
```json
[
	{ "id": "<uuid>", "@type": "ComponentSchema", ... },
]
```

---

### List Relationships

**GET** `/relationships`

Lists all explicit relationships between metamodels. Supports filtering by type, source, or target.

**Query Parameters:**
- `relationship_type` (optional): Filter by relationship type
- `source_id` (optional): Filter by source entity
- `target_id` (optional): Filter by target entity

**Response Example:**
```json
[
	{ "id": "<relationship-uuid>", "source_id": "<workflow-uuid>", "target_id": "<component-uuid>", "relationship_type": "contains" },
]
```

---

### Update Metadata

**PUT** `/metadata/{metadata_id}`

Updates an existing metadata document. Only mutable fields can be updated.

---

### Deprecate Metadata

**POST** `/metadata/{metadata_id}/deprecate`

Soft-deprecates a metadata document.

---

### Get Metadata Version History

**GET** `/metadata/{metadata_id}/versions`

Returns all historical versions of a metadata document.

---

## Error Handling

All errors return a JSON object with a `detail` field and appropriate HTTP status code.

**Example:**
```json
{
	"detail": "Metadata not found."
}
```

## Authentication & Rate Limiting

Authentication and rate limiting are stubbed for future implementation. All endpoints currently allow anonymous access.

## OpenAPI Schema

The full OpenAPI schema is available at `/openapi.json` when running the service.

## Example Usage (curl)

```sh
curl -X POST https://<your-domain>/metadata \
	-H 'Content-Type: application/json' \
	-d '{"@type": "ComponentSchema", "@context": {"@vocab": "http://example.com/"}, "data": {"foo": "bar"}}'
```

## Example Usage (Python requests)

```python
import requests
resp = requests.post(
		"https://<your-domain>/metadata",
		json={
				"@type": "ComponentSchema",
				"@context": {"@vocab": "http://example.com/"},
				"data": {"foo": "bar"}
		}
)
print(resp.json())
```
