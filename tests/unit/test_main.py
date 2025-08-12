
# Patch sys.path at the very top for import resolution

import sys
import os

test_dir = os.path.dirname(__file__)
repo_root = os.path.abspath(os.path.join(test_dir, '../..'))
domain_repo_path = os.path.join(repo_root, 'domain-repository')
svc_src_path = os.path.join(repo_root, 'metadata-registry-svc', 'src')
if domain_repo_path not in sys.path:
    sys.path.insert(0, domain_repo_path)
if svc_src_path not in sys.path:
    sys.path.insert(0, svc_src_path)

print('DEBUG sys.path:', sys.path)

import pytest
from unittest.mock import patch
from domain_repository.core.registry import MetamodelRegistry
from domain_repository.operational.workflow import Workflow
from domain_repository.operational.component import Component
# --- Relationship API Tests ---


def test_openapi_relationships_endpoints():
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    paths = resp.json()["paths"].keys()
    assert "/relationships" in paths
    assert any(p.startswith("/relationships") for p in paths)

# Patch the global registry for relationship tests using app state for DI
@pytest.fixture(autouse=True)
def mock_registry():
    from metadata_registry_svc.main import app
    reg = MetamodelRegistry()
    app.state.registry = reg
    yield reg
    app.state.registry = None

def register_entity_with_registry(metamodel_type, name=None, reg=None):
    # Register entity via API and also in the registry for relationship tests
    resp = client.post("/metadata", json=make_entity_payload(metamodel_type, name))
    assert resp.status_code == 201
    entity_id = resp.json()["id"]
    # Register in the registry for relationship manager
    if reg:
        if metamodel_type == "Workflow":
            reg.register_instance(Workflow(id=entity_id, name=name or "Test Workflow"))
        elif metamodel_type == "Component":
            reg.register_instance(Component(id=entity_id, name=name or "Test Component"))
    return entity_id

import sys
import os
from uuid import uuid4
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../domain-repository')))
from fastapi.testclient import TestClient
from metadata_registry_svc.main import app
print('DEBUG app location:', app.__module__, app)

client = TestClient(app)


def make_doc_dict(**kwargs):
    return {
        "@type": "ComponentSchema",
        "@context": {"@vocab": "http://example.com/"},
        "data": {"name": "Test Component", **kwargs},
    }


def test_register_metadata():
    doc = make_doc_dict()
    resp = client.post("/metadata", json=doc)
    assert resp.status_code == 201
    assert resp.json()["@type"] == "ComponentSchema"


def test_register_duplicate_metadata():
    doc = make_doc_dict()
    resp1 = client.post("/metadata", json=doc)
    assert resp1.status_code == 201
    # Use returned id for duplicate
    doc["id"] = resp1.json()["id"]
    resp2 = client.post("/metadata", json=doc)
    assert resp2.status_code == 409


def test_get_metadata():
    doc = make_doc_dict()
    resp = client.post("/metadata", json=doc)
    id_ = resp.json()["id"]
    get_resp = client.get(f"/metadata/{id_}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == id_


def test_get_metadata_not_found():
    resp = client.get(f"/metadata/{uuid4()}")
    assert resp.status_code == 404


# --- Relationship API Tests ---
from domain_repository.core.relationships import RelationshipType

def make_entity_payload(metamodel_type, name=None):
    # Helper to create a valid entity payload for registration
    allowed_types = ["ComponentSchema", "ExpectationSchema", "ProtocolSchema", "WorkflowSchema"]
    if metamodel_type == "Workflow":
        type_val = "WorkflowSchema"
        data = {"name": name or f"{metamodel_type}-{uuid4()}"}
    elif metamodel_type == "Component":
        type_val = "ComponentSchema"
        data = {"name": name or f"{metamodel_type}-{uuid4()}"}
    elif metamodel_type == "Protocol":
        type_val = "ProtocolSchema"
        data = {"name": name or f"{metamodel_type}-{uuid4()}"}
    elif metamodel_type == "Expectation":
        type_val = "ExpectationSchema"
        data = {"name": name or f"{metamodel_type}-{uuid4()}", "expectation_type": "SomeType"}
    else:
        type_val = "ComponentSchema"
        data = {"name": name or f"{metamodel_type}-{uuid4()}"}
    return {
        "@type": type_val,
        "@context": {"@vocab": "http://example.com/"},
        "data": data
    }

def register_entity(metamodel_type, name=None):
    resp = client.post("/metadata", json=make_entity_payload(metamodel_type, name))
    assert resp.status_code == 201
    return resp.json()["id"]

def test_create_relationship_and_get(mock_registry):
    # Create source and target entities and register in registry
    workflow_id = register_entity_with_registry("Workflow", reg=mock_registry)
    component_id = register_entity_with_registry("Component", reg=mock_registry)
    # Create a valid relationship
    rel_req = {
        "source_id": workflow_id,
        "target_id": component_id,
        "relationship_type": "contains"
    }
    rel_resp = client.post("/relationships", json=rel_req)
    assert rel_resp.status_code == 201
    rel_data = rel_resp.json()
    assert rel_data["source_id"] == workflow_id
    assert rel_data["target_id"] == component_id
    assert rel_data["relationship_type"] == "contains"
    # Get by ID
    rel_id = rel_data["id"]
    get_resp = client.get(f"/relationships/{rel_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == rel_id

def test_create_relationship_invalid_type(mock_registry):
    workflow_id = register_entity_with_registry("Workflow", reg=mock_registry)
    component_id = register_entity_with_registry("Component", reg=mock_registry)
    # Invalid relationship type
    rel_req = {
        "source_id": workflow_id,
        "target_id": component_id,
        "relationship_type": "invalid_type"
    }
    rel_resp = client.post("/relationships", json=rel_req)
    assert rel_resp.status_code == 422  # FastAPI validation error

def test_create_relationship_invalid_entities():
    # Use random UUIDs for non-existent entities
    rel_req = {
        "source_id": str(uuid4()),
        "target_id": str(uuid4()),
        "relationship_type": "contains"
    }
    rel_resp = client.post("/relationships", json=rel_req)
    assert rel_resp.status_code == 404
    assert "not found" in rel_resp.json()["detail"].lower()

def test_list_relationships(mock_registry):
    workflow_id = register_entity_with_registry("Workflow", reg=mock_registry)
    component_id = register_entity_with_registry("Component", reg=mock_registry)
    # Create relationship
    rel_req = {
        "source_id": workflow_id,
        "target_id": component_id,
        "relationship_type": "contains"
    }
    rel_resp = client.post("/relationships", json=rel_req)
    rel_id = rel_resp.json()["id"]
    # List all
    list_resp = client.get("/relationships")
    assert list_resp.status_code == 200
    rels = list_resp.json()
    assert any(r["id"] == rel_id for r in rels)
    # Filter by source_id
    filter_resp = client.get(f"/relationships?source_id={workflow_id}")
    assert filter_resp.status_code == 200
    filtered = filter_resp.json()
    assert all(r["source_id"] == workflow_id for r in filtered)

def test_get_relationship_not_found():
    resp = client.get(f"/relationships/{uuid4()}")
    assert resp.status_code == 404
