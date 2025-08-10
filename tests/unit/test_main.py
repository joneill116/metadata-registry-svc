from fastapi.testclient import TestClient
from metadata_registry_svc.main import app
from uuid import uuid4

client = TestClient(app)


def make_doc_dict(**kwargs):
    return {
        "@type": "ComponentSchema",
        "@context": {},
        "data": {"foo": "bar"},
        **kwargs,
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
