import pytest
import os
import json
import pathlib
from uuid import uuid4

from modules.chunks.application.use_cases.chunk_document import ChunkDocumentUseCase
from modules.documents.domain.entities.document import Document

@pytest.fixture
def use_case():
    return ChunkDocumentUseCase()

@pytest.fixture
def dummy_document():
    # Cria um documento simples para teste (tipo genérico)
    return Document(
        document_id=str(uuid4()),
        file_name="dummy_test_doc.pdf",
        document_type="generic",
        source_path="/fake/path/dummy_test_doc.pdf",
        text="Este é um parágrafo de teste.\nEste é outro parágrafo de teste.",
        metadata={"processed_at": "2026-06-15T00:00:00"}
    )

def test_chunk_document_saves_json(use_case, dummy_document, tmp_path, monkeypatch):
    # Interceptar Path para apontar "data/processed" para tmp_path
    original_path = pathlib.Path
    def mock_path(*args, **kwargs):
        if args and args[0] == "data/processed":
            return tmp_path / "data/processed"
        return original_path(*args, **kwargs)
        
    monkeypatch.setattr("modules.chunks.application.use_cases.chunk_document.Path", mock_path)

    # Executa o fatiamento
    chunks = use_case.execute(dummy_document)

    # Verifica os chunks na memória
    assert len(chunks) > 0
    assert chunks[0].document_id == dummy_document.document_id
    assert chunks[0].content is not None

    # Verifica se o arquivo JSON foi criado fisicamente no tmp_path
    processed_dir = tmp_path / "data/processed"
    json_file = processed_dir / "dummy_test_doc.pdf_chunks.json"
    
    # O ChunkDocumentUseCase usa Path(document.file_name).stem, que vira "dummy_test_doc_chunks.json"
    # Vamos verificar o nome exato. No código original, é:
    # json_path = processed_dir / f"{Path(document.file_name).stem}_chunks.json"
    json_file = processed_dir / "dummy_test_doc_chunks.json"
    
    assert json_file.exists(), f"O arquivo JSON {json_file} não foi criado na pasta processed!"

    # Lê e valida a estrutura do JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Garante que é uma lista de chunks
    assert isinstance(data, list)
    assert len(data) == len(chunks)
    
    # Valida as chaves do primeiro chunk
    first_chunk = data[0]
    assert "chunk_id" in first_chunk
    assert "document_id" in first_chunk
    assert "chunk_index" in first_chunk
    assert "content" in first_chunk
    assert "metadata" in first_chunk
    assert first_chunk["document_id"] == dummy_document.document_id
