import pytest
from datetime import datetime
from pydantic import ValidationError
from metadata_registry_svc.models import MetadataDocument


def test_metadata_document_missing_context():
    with pytest.raises(ValidationError):
        MetadataDocument(**{"@type": "ComponentSchema"}, data={"foo": "bar"})


def test_metadata_document_missing_type():
    with pytest.raises(ValidationError):
        MetadataDocument(
            **{"@context": {"@vocab": "http://example.com/"}}, data={"foo": "bar"}
        )


def test_metadata_document_invalid_context_type():
    with pytest.raises(ValidationError):
        MetadataDocument(
            **{"@type": "ComponentSchema", "@context": 123}, data={"foo": "bar"}
        )


def test_metadata_document_invalid_type_value():
    with pytest.raises(ValidationError):
        MetadataDocument(
            **{"@type": "NotAValidType", "@context": {"@vocab": "http://example.com/"}},
            data={"foo": "bar"}
        )


def test_metadata_document_is_deprecated_flag():
    doc = MetadataDocument(
        **{"@type": "ComponentSchema", "@context": {"@vocab": "http://example.com/"}},
        data={"foo": "bar"},
        is_deprecated=True
    )
    assert doc.is_deprecated is True


def test_metadata_document_missing_data_defaults():
    doc = MetadataDocument(
        **{"@type": "ComponentSchema", "@context": {"@vocab": "http://example.com/"}}
    )
    assert doc.data == {}


def test_metadata_document_valid():
    doc = MetadataDocument(
        **{"@type": "ComponentSchema", "@context": {"@vocab": "http://example.com/"}},
        data={"foo": "bar"},
        owner="alice",
        tags=["tag1", "tag2"]
    )
    assert doc.type == "ComponentSchema"
    assert doc.context == {"@vocab": "http://example.com/"}
    assert doc.version == 1
    assert isinstance(doc.created_at, datetime)
    assert isinstance(doc.updated_at, datetime)
    assert doc.owner == "alice"
    assert doc.tags == ["tag1", "tag2"]
    assert doc.data == {"foo": "bar"}
    assert not doc.is_deprecated


def test_metadata_document_type_literal():
    with pytest.raises(ValidationError):
        MetadataDocument(
            **{"@type": "InvalidType", "@context": {"@vocab": "http://example.com/"}},
            data={}
        )


def test_metadata_document_data_size_limit():
    big_data = {"x": "y" * 10000}
    with pytest.raises(ValidationError):
        MetadataDocument(
            **{
                "@type": "ComponentSchema",
                "@context": {"@vocab": "http://example.com/"},
            },
            data=big_data
        )


def test_metadata_document_default_values():
    doc = MetadataDocument(
        **{"@type": "ProtocolSchema", "@context": {"@vocab": "http://example.com/"}},
        data={}
    )
    assert doc.version == 1
    assert doc.owner is None
    assert doc.tags == []
    assert not doc.is_deprecated
