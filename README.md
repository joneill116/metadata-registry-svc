

# [DEPRECATED] Please see the root-level README.md for all documentation and usage. This file is intentionally left blank.

**A world-class, extensible platform for registering, validating, and discovering polymorphic metamodels, metadata, and semantic relationships for modern data and workflow architectures.**

## Vision
Enable organizations to model, govern, and orchestrate any domain—workflows, components, expectations, protocols, and solutions—using standards-based, linked, and versioned metadata. Designed for extensibility, interoperability, and business agility.

## Key Features
- **Polymorphic Metamodel Registry:** Register, version, and deprecate workflow, component, expectation, protocol, and solution metamodels using a polymorphic, registry-based architecture.
- **Type-Safe Relationships:** Traverse and query explicit, validated relationships between all entities (e.g., which workflows use which components, protocols, etc.).
- **Ontology/Semantic Features:** Register and query semantic tags, ontology mappings, external references, constraints, and inheritance for all metamodels and metadata.
- **JSON-LD Native:** All metadata and metamodels are stored and served as JSON-LD, enabling semantic interoperability and linked data.
- **Instance Management:** Create and manage workflow/component/expectation/protocol instances, always linked to their metamodels.
- **Versioning & Evolution:** Full support for versioned schemas, deprecation, and migration.
- **Validation:** Pydantic-powered validation ensures only well-formed, standards-compliant metadata is registered.
- **OpenAPI & Self-Documentation:** Interactive API docs for all endpoints.
- **Extensible & Modular:** Add new domains, types, and relationships with minimal code changes.
- **Ready for Triple Store:** Designed for integration with RDF triple stores and SPARQL for advanced graph/semantic queries.

## Architecture Overview

```
┌──────────────────────────────┐
│   Domain Repository (Polymorphic Metamodels) │
└─────────────┬────────────────┘
			  │
			  ▼
┌──────────────────────────────┐
│ Metadata Registry Service    │
│  - Registers & validates     │
│  - Exposes API for CRUD      │
│  - Links all concepts        │
└─────────────┬────────────────┘
			  │
			  ▼
┌──────────────────────────────┐
│  Downstream Solutions        │
│  (e.g., Portfolio Mgmt)      │
└─────────────┬────────────────┘
			  │
			  ▼
┌──────────────────────────────┐
│  Workflow/Component Instances│
└──────────────────────────────┘
```

## Example Use Cases
- Register a new workflow template (e.g., Regulatory Workflow) with recommended components, expectations, and protocols using the polymorphic service layer.
- Users create workflow instances by selecting a template and customizing components/configs as needed.
- Query all workflows using a specific protocol or expectation via the relationship manager.
- Version and deprecate metamodels as business needs evolve.
- Integrate with a triple store for semantic queries and knowledge graph analytics.

## Integration with Domain Repository
The Metadata Registry Service now integrates with the `domain-repository` package, which provides:
- Polymorphic base classes for all metamodels
- Type-safe relationship management
- Central registry for all metamodels and relationships
- High-level service API for creating, linking, and querying metamodels

### Example: Registering and Linking Metamodels
```python
from domain_repository import polymorphic_service

## Example: Relationship-Centric Linking

# Create protocol, expectation, and component (no direct references)
protocol = polymorphic_service.create_protocol(
	name="REST API Protocol",
	specification_url="https://restfulapi.net/",
	semantic_tags=["api", "rest"],
	ontology_mappings={"skos:exactMatch": "https://schema.org/WebAPI"},
	external_references=["https://schema.org/WebAPI"],
	constraints=[{"property": "specification_url", "pattern": "^https?://"}]
)
expectation = polymorphic_service.create_expectation(
	name="Data Quality",
	validation_rules=["non_null_check"],
	semantic_tags=["quality", "validation"],
	ontology_mappings={"skos:exactMatch": "https://schema.org/PropertyValue"}
)
component = polymorphic_service.create_component(
	name="Acquisition",
	semantic_tags=["acquisition", "data"],
	ontology_mappings={"skos:broader": "https://schema.org/Action"}
)

# Create workflow (no component_ids field)
workflow = polymorphic_service.create_workflow(
	name="Data Pipeline",
	semantic_tags=["pipeline", "workflow"]
)

# Link entities via explicit relationships
polymorphic_service.create_relationship(
	source_id=workflow.id,
	target_id=component.id,
	relationship_type="contains"
)
polymorphic_service.create_relationship(
	source_id=component.id,
	target_id=protocol.id,
	relationship_type="implements"
)
polymorphic_service.create_relationship(
	source_id=component.id,
	target_id=expectation.id,
	relationship_type="fulfills"
)

# Export the complete JSON-LD graph
print(polymorphic_service.export_complete_jsonld_graph())
```

## Quickstart
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.metadata_registry_svc.main:app --reload
```

## Extensibility & Best Practices
- **Add new metamodels:** Extend the domain library and register new types via the API.
- **All entity connections are managed via explicit Relationship objects—never direct fields.**
- **Versioning:** Use the version field to evolve schemas without breaking existing instances.
- **Governance:** Use tags, owner, and deprecation fields for audit and compliance.
- **Validation:** All data is validated both client- and server-side using Pydantic and JSON-LD.
- **Integration:** Designed for easy integration with orchestration engines, data mesh, and knowledge graph platforms.

## Documentation
- See `docs/ARCHITECTURE.md` for detailed architecture and design principles.
- See `docs/API.md` for full API reference and examples.
- All JSON-LD and API payloads reflect the decoupled, relationship-centric model.

---
*Built for world-class engineers, designers, and ontologists who demand clarity, flexibility, and future-proof data architecture.*

## Migration Note
If upgrading from a previous version, remove all direct reference fields (e.g., `component_ids`, `protocol_id`, `expectation_id`) from your code and use explicit relationships instead.

## Validation Checklist (World-Class Ontology Review)
- [x] All entity connections are explicit relationships
- [x] Ontology/semantic fields and provenance are present
- [x] SHACL/OWL constraints supported
- [x] JSON-LD serialization for all entities and relationships
- [x] Registry and relationship manager are central to all operations
