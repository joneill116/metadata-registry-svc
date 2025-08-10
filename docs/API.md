
# Metadata Registry Service API Reference

This document provides a comprehensive overview of the REST API for the Metadata Registry Service.
All endpoints are JSON-based and follow RESTful conventions. Authentication and rate limiting are stubbed for future implementation.

## Base URL

```
https://<your-domain>/
```

## Endpoints

### Register Metadata

**POST** `/metadata`

Registers a new metadata document.

**Request Body Example:**
```json
{
	"@type": "ComponentSchema",
	"@context": {"@vocab": "http://example.com/"},
	"data": {"foo": "bar"},
	"owner": "alice",
	"tags": ["tag1", "tag2"]
}
```

**Response Example:**
```json
{
	"id": "<uuid>",
	"@type": "ComponentSchema",
	"@context": {"@vocab": "http://example.com/"},
	"data": {"foo": "bar"},
	"owner": "alice",
	"tags": ["tag1", "tag2"],
	"version": 1,
	"created_at": "2025-08-10T12:00:00Z",
	"updated_at": "2025-08-10T12:00:00Z",
	"is_deprecated": false
}
```

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
