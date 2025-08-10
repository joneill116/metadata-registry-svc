# Metadata Registry Service Architecture

This document describes the architecture, design principles, and integration patterns of the Metadata Registry Service. The service is designed for extensibility, clarity, and reliability, serving as the single source of truth for all metadata schemas and definitions in the platform.

## High-Level Overview

- **Purpose:** Central registry for all metadata schemas, definitions, and contracts.
- **Design:** Modular, event-driven, and integration-ready.
- **Principles:** Single source of truth, separation of concerns, testability, and extensibility.

## Service Relationship Diagram

## Service Relationship Diagram

```
				+--------------------------+
				|  metadata-registry-svc   |
				|  (schemas, definitions)  |
				+-----------+--------------+
						^
						|
	  +---------------------------+---------------------------+
	  |                           |                           |
	  |                           |                           |
  +-----+-----+             +-------+-------+           +-------+-------+
  | component |             | expectation   |           | protocol      |
  | registry  |             | registry      |           | registry      |
  |   svc     |             |   svc         |           |   svc         |
  +-----+-----+             +-------+-------+           +-------+-------+
	  |                           |                           |
	  |                           |                           |
	  v                           v                           v
   (references schemas,      (references schemas,         (references schemas,
    contracts, types)         rules, types)                message formats)
```


**Legend:**
- All domain registries reference schemas/definitions in the metadata-registry-svc.
- metadata-registry-svc is the single source of truth for all metadata.
- Each registry (component, expectation, protocol) is decoupled and can evolve independently, but all depend on the metadata-registry-svc for schema validation and discovery.

## Key Components

- **metadata-registry-svc:**
	- Stores and versions all metadata schemas and definitions.
	- Provides REST API for CRUD, versioning, and deprecation.
	- Emits events for registry changes (future extension).
- **Domain registries (component, expectation, protocol):**
	- Reference and validate against schemas in metadata-registry-svc.
	- Implement domain-specific logic and workflows.

## Design Principles

- **Modularity:** All core logic is separated from adapters and integrations for testability and maintainability.
- **Event-Driven:** Designed to emit and consume events for registry changes and integrations (future-proof).
- **Extensibility:** New schema types and registry domains can be added with minimal changes.
- **Observability:** Logging, metrics, and health endpoints are built-in for production readiness.
- **Governance:** Versioning, soft deletion, and auditability are first-class features.

## Integration Points

- **API:** RESTful endpoints for all registry operations.
- **Events:** (Planned) Event hooks for registry changes, deprecations, and versioning.
- **Adapters:** Easily integrate with databases, message brokers, and external services.

## Contributor Guide

- **How to extend:** Add new schema types by updating the allowed types in the model and API docs.
- **Testing:** 100% unit test coverage is enforced; use pytest and follow the test structure in `tests/`.
- **Code style:** Black and flake8 are enforced in CI/CD; see `.flake8` and `pyproject.toml` for config.
- **Docs:** Update this file and `API.md` for any architectural or API changes.

## Glossary

- **Schema:** A JSON-LD definition describing a component, expectation, or protocol.
- **Registry:** A service that stores, versions, and governs schemas.
- **Deprecation:** Soft deletion of a schema, retaining history and discoverability.

## FAQ

**Q: How do I add a new schema type?**
A: Update the allowed types in the model, add API documentation, and write tests for the new type.

**Q: How do I integrate a new domain registry?**
A: Reference the metadata-registry-svc for schema validation and discovery; follow the integration patterns in this document.
