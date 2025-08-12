import pytest
from uuid import uuid4
from metadata_registry_svc.models import MetadataDocument
from metadata_registry_svc import service


def test_list_metadata_type_filter():
    doc1 = service.MetadataDocument(
        **{"@type": "ComponentSchema", "@context": {"@vocab": "http://example.com/"}},
        data={"name": "Test Component"},
    )
    doc2 = service.MetadataDocument(
        **{"@type": "ExpectationSchema", "@context": {"@vocab": "http://example.com/"}},
        data={"name": "Test Expectation", "expectation_type": "SomeType"},
    )
    service.register_metadata(doc1)
    service.register_metadata(doc2)
    # Should return only doc1
    results = service.list_metadata(type="ComponentSchema")
    assert doc1 in results and doc2 not in results
    # Should return only doc2
    results = service.list_metadata(type="ExpectationSchema")
    assert doc2 in results and doc1 not in results
    # Should return empty for type not present
    results = service.list_metadata(type="ProtocolSchema")
    assert results == []


def test_list_metadata_tags_no_match():
    doc = make_doc(tags=["a", "b"])
    service.register_metadata(doc)
    results = service.list_metadata(tags=["z"])
    assert results == []


def test_list_metadata_pagination_empty():
    docs = [make_doc(owner=f"user{i}") for i in range(3)]
    for d in docs:
        service.register_metadata(d)
    paged = service.list_metadata(limit=2, offset=10)
    assert paged == []


def test_list_metadata_all_filters_no_match():
    doc = make_doc(tags=["a"], owner="bob")
    service.register_metadata(doc)
    results = service.list_metadata(type="ExpectationSchema", owner="alice", tags=["z"])
    assert results == []


def test_update_immutable_field_raises():
    doc = make_doc()
    service.register_metadata(doc)
    with pytest.raises(service.MetadataRegistryError) as exc:
        service.update_metadata(doc.id, {"id": "new-id"})
    assert "immutable field" in str(exc.value)


def test_list_metadata_empty_store():
    # Store is cleared by fixture
    assert service.list_metadata() == []


def test_list_metadata_with_tags_filter():
    doc1 = make_doc(tags=["a", "b"])
    doc2 = make_doc(tags=["b", "c"])
    service.register_metadata(doc1)
    service.register_metadata(doc2)
    results = service.list_metadata(tags=["b"])
    assert doc1 in results and doc2 in results
    results = service.list_metadata(tags=["a"])
    assert doc1 in results and doc2 not in results
    results = service.list_metadata(tags=["c"])
    assert doc2 in results and doc1 not in results


def test_list_metadata_pagination():
    docs = [make_doc(owner=f"user{i}") for i in range(10)]
    for d in docs:
        service.register_metadata(d)
    paged = service.list_metadata(limit=3, offset=2)
    assert len(paged) == 3
    assert paged == docs[2:5]


def test_register_metadata_with_all_optional_fields():
    doc = make_doc(owner="bob", tags=["x", "y"])
    out = service.register_metadata(doc)
    assert out.owner == "bob"
    assert out.tags == ["x", "y"]


def test_register_metadata_with_minimal_fields():
    doc = MetadataDocument(
        **{"@type": "ComponentSchema", "@context": {"@vocab": "http://example.com/"}},
        data={"name": "Test Component"},
    )
    out = service.register_metadata(doc)
    assert out.owner is None
    assert out.tags == []


def test_update_deprecated_metadata_raises():
    doc = make_doc()
    service.register_metadata(doc)
    service.deprecate_metadata(doc.id)
    with pytest.raises(service.MetadataRegistryError):
        service.update_metadata(doc.id, {"data": {"foo": "baz"}})


def test_deprecate_already_deprecated_metadata():
    doc = make_doc()
    service.register_metadata(doc)
    service.deprecate_metadata(doc.id)
    # Should be idempotent (no error)
    service.deprecate_metadata(doc.id)
    assert service.get_metadata(doc.id).is_deprecated


def test_get_metadata_versions_not_found():
    from uuid import uuid4

    with pytest.raises(service.MetadataRegistryError):
        service.get_metadata_versions(uuid4())


@pytest.fixture(autouse=True)
def clear_store():
    service._metadata_store.clear()
    service._metadata_versions.clear()


def make_doc(**kwargs):
    # Always provide a valid 'name' for ComponentSchema
    data = kwargs.pop('data', None)
    if data is None:
        data = {"name": "Test Component"}
    else:
        data = {"name": "Test Component", **data}
    return MetadataDocument(
        **{"@type": "ComponentSchema", "@context": {"@vocab": "http://example.com/"}},
        data=data,
        **kwargs,
    )


def test_register_and_get_metadata():
    doc = make_doc()
    out = service.register_metadata(doc)
    assert out == doc
    fetched = service.get_metadata(doc.id)
    assert fetched == doc


def test_register_duplicate_metadata():
    doc = make_doc()
    service.register_metadata(doc)
    with pytest.raises(service.MetadataRegistryError):
        service.register_metadata(doc)


def test_get_metadata_not_found():
    with pytest.raises(service.MetadataRegistryError):
        service.get_metadata(uuid4())


def test_update_metadata():
    doc = make_doc()
    service.register_metadata(doc)
    # Always include required fields in update
    updated = service.update_metadata(doc.id, {"data": {"name": doc.data["name"], "foo": "baz"}})
    assert updated.data["foo"] == "baz"
    assert updated.version == 2
    assert updated.updated_at > doc.updated_at


def test_update_metadata_not_found():
    with pytest.raises(service.MetadataRegistryError):
        service.update_metadata(uuid4(), {"data": {"foo": "baz"}})


def test_deprecate_metadata():
    doc = make_doc()
    service.register_metadata(doc)
    service.deprecate_metadata(doc.id)
    assert service.get_metadata(doc.id).is_deprecated


def test_list_metadata():
    docs = [make_doc(owner=f"user{i}") for i in range(5)]
    for d in docs:
        service.register_metadata(d)
    listed = service.list_metadata()
    assert len(listed) == 5


def test_get_metadata_versions():
    doc = make_doc()
    service.register_metadata(doc)
    # Always include required fields in update
    service.update_metadata(doc.id, {"data": {"name": doc.data["name"], "foo": "baz"}})
    versions = service.get_metadata_versions(doc.id)
    assert len(versions) == 2
    assert versions[0].version == 1
    assert versions[1].version == 2


def test_list_metadata_include_deprecated():
    doc_active = make_doc()
    doc_deprecated = make_doc()
    service.register_metadata(doc_active)
    service.register_metadata(doc_deprecated)
    service.deprecate_metadata(doc_deprecated.id)
    # By default, deprecated should be excluded
    results = service.list_metadata()
    assert doc_active in results
    assert all(not d.is_deprecated for d in results)
    # With include_deprecated=True, both should be present
    results = service.list_metadata(include_deprecated=True)
    deprecated_in_store = service.get_metadata(doc_deprecated.id)
    assert doc_active in results
    assert deprecated_in_store in results
    assert any(d.is_deprecated for d in results)
