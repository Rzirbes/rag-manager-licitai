import pytest
import os
from modules.documents.infra.extractors.pypdf_document_extractor import PyPdfDocumentExtractor

@pytest.fixture
def extractor():
    return PyPdfDocumentExtractor()

@pytest.fixture
def valid_pdf_path():
    path = os.path.join(os.path.dirname(__file__), "../../../../fixtures/test_valid.pdf")
    return os.path.normpath(path)

@pytest.fixture
def invalid_extension_path():
    path = os.path.join(os.path.dirname(__file__), "../../../../fixtures/test_invalid_format.docx")
    return os.path.normpath(path)

def test_extract_text_valid_pdf(extractor, valid_pdf_path):
    text, metadata = extractor.extract_text(valid_pdf_path)
    assert text is not None
    assert len(text.strip()) > 0
    assert "page_count" in metadata
    assert metadata["page_count"] > 0

def test_extract_text_invalid_extension(extractor, invalid_extension_path):
    with pytest.raises(ValueError, match="O arquivo não é um documento PDF"):
        extractor.extract_text(invalid_extension_path)

def test_extract_text_non_existent_file(extractor):
    with pytest.raises(FileNotFoundError):
        extractor.extract_text("non_existent_file.pdf")
