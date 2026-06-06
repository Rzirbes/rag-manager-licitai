import pytest
from unittest.mock import Mock
import os

from modules.documents.application.use_cases.extract_document_text import ExtractDocumentTextUseCase
from modules.documents.domain.repositories.document_extractor_repository import DocumentExtractorRepository
from modules.documents.application.exceptions import DocumentExtractionError

@pytest.fixture
def mock_extractor():
    return Mock(spec=DocumentExtractorRepository)

@pytest.fixture
def use_case(mock_extractor):
    return ExtractDocumentTextUseCase(extractor=mock_extractor)

@pytest.fixture
def valid_pdf_path():
    path = os.path.join(os.path.dirname(__file__), "../../../../fixtures/test_valid.pdf")
    return os.path.normpath(path)

def test_execute_success(use_case, mock_extractor, valid_pdf_path):
    # configurar comportamento simulado
    mock_extractor.extract_text.return_value = ("Sample extracted text.", {"page_count": 1})
    
    # execução 
    document = use_case.execute(valid_pdf_path)
    
    # verificação
    assert document is not None
    assert document.text == "Sample extracted text."
    assert "page_count" in document.metadata
    assert document.metadata["page_count"] == 1
    assert "document_size" in document.metadata
    assert document.metadata["document_size"] == len("Sample extracted text.")
    assert "file_size_bytes" in document.metadata
    assert "processed_at" in document.metadata

def test_execute_handles_extraction_error(use_case, mock_extractor, valid_pdf_path):
    # simular um erro do extrator
    mock_extractor.extract_text.side_effect = ValueError("Some weird error")
    
    # verificar se a exceção de domínio é levantada
    with pytest.raises(DocumentExtractionError, match="Erro ao extrair texto"):
        use_case.execute(valid_pdf_path)
