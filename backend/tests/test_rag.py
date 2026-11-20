import json

from app.rag.ingest_faq import ingest_faq
from app.rag.ingest_pdf import ingest_pdf
from app.rag.retriever import retrieve_context, retrieve_passages
from app.rag.store import get_client, get_collection
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject


def test_missing_and_empty_index_do_not_invent_context():
    assert retrieve_context("inscription") == ""
    assert get_client().list_collections() == []
    get_collection(create=True)
    assert retrieve_passages("inscription") == []
    assert retrieve_passages("  ") == []


def test_faq_idempotence_updates_and_persistence(isolated_settings):
    path = isolated_settings.data_path / "faq.json"
    items = [
        {"question": "inscription", "answer": "La procédure est en ligne."},
        {"question": "bibliothèque", "answer": "Ouverture à 8h."},
    ]
    path.write_text(json.dumps(items), encoding="utf-8")
    assert ingest_faq(path) == 2
    assert ingest_faq(path) == 2
    assert get_collection().count() == 2
    found = retrieve_passages("inscription")
    assert len(found) == 1
    assert "en ligne" in found[0].text
    assert found[0].source == "faq.json"
    items = [{"question": "inscription", "answer": "Procédure modifiée."}]
    path.write_text(json.dumps(items), encoding="utf-8")
    ingest_faq(path)
    assert get_collection().count() == 1
    # Re-open the persistent client, rather than relying on the Python cache.
    get_client.cache_clear()
    assert "modifiée" in retrieve_context("inscription")
    assert retrieve_passages("bibliothèque") == []


def test_pdf_ingestion_and_faq_share_collection(isolated_settings):
    path = isolated_settings.data_path / "guide.pdf"
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})}
    )
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 10 200 Td (Examens en juin.) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(stream)
    writer.write(path)
    assert ingest_pdf(path) == 1
    assert ingest_pdf(path) == 1
    faq = isolated_settings.data_path / "faq.json"
    faq.write_text('[{"question":"inscription", "answer":"En ligne"}]')
    ingest_faq(faq)
    assert get_collection().count() == 2
    found = retrieve_passages("examen")
    assert len(found) == 1
    assert found[0].source == "guide.pdf"
    assert found[0].page == 1
    assert "juin" in found[0].text


def test_top_k_and_context_budget(isolated_settings):
    collection = get_collection(create=True)
    collection.upsert(
        ids=["a", "b", "c"],
        documents=["inscription " * 100] * 3,
        metadatas=[{"source": "faq.json"}] * 3,
    )
    isolated_settings.rag_top_k = 2
    isolated_settings.rag_context_chars = 1000
    found = retrieve_passages("inscription")
    assert len(found) <= 2
    assert sum(len(p.text) for p in found) <= 1000


def test_invalid_faq_does_not_overwrite_existing_index(isolated_settings):
    import pytest
    from pydantic import ValidationError

    path = isolated_settings.data_path / "faq.json"
    path.write_text('[{"question":"inscription", "answer":"En ligne"}]')
    ingest_faq(path)
    path.write_text('[{"question":"inscription", "answer":"   "}]')
    with pytest.raises(ValidationError):
        ingest_faq(path)
    assert get_collection().count() == 1
