import pytest
import os
from modules.documents.infra.extractors.smart_document_extractor import SmartDocumentExtractor

@pytest.fixture
def smart_extractor():
    return SmartDocumentExtractor()

@pytest.fixture
def valid_pdf_path():
    path = os.path.join(os.path.dirname(__file__), "../../../../fixtures/test_valid.pdf")
    return os.path.normpath(path)

@pytest.fixture
def invalid_extension_path():
    # A text file masquerading as docx, meaning all real extractors will fail to parse it.
    path = os.path.join(os.path.dirname(__file__), "../../../../fixtures/test_invalid_format.docx")
    return os.path.normpath(path)

def test_smart_extractor_valid_document(smart_extractor, valid_pdf_path):
    text, metadata = smart_extractor.extract_text(valid_pdf_path)
    assert text is not None
    assert len(text.strip()) > 0
    assert "page_count" in metadata

def test_smart_extractor_unsupported_format(smart_extractor, invalid_extension_path):
    with pytest.raises(ValueError, match="Nenhum extrator conseguiu extrair o texto do arquivo"):
        smart_extractor.extract_text(invalid_extension_path)

def test_smart_extractor_non_existent_file(smart_extractor):
    with pytest.raises(FileNotFoundError):
        smart_extractor.extract_text("this_file_does_not_exist.pdf")
