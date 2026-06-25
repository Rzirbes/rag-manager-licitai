import pytest
import os
import json
import pathlib
from unittest.mock import MagicMock

from modules.embedding.application.use_cases.embedding_convert import GenerateEmbeddingsUseCase
from modules.embedding.domain.repositories.embedding_provider_repository import EmbeddingProviderRepository
from modules.embedding.domain.repositories.vector_db_repository import VectorDbRepository

@pytest.fixture
def mock_provider():
    provider = MagicMock(spec=EmbeddingProviderRepository)
    # Sempre retorna um vetor de [0.99, 0.99] para facilitar o teste
    provider.generate_embeddings_batch.return_value = [[0.99, 0.99], [0.99, 0.99]]
    return provider

@pytest.fixture
def mock_vector_db():
    return MagicMock(spec=VectorDbRepository)

@pytest.fixture
def use_case(mock_provider, mock_vector_db):
    return GenerateEmbeddingsUseCase(provider=mock_provider, vector_db=mock_vector_db)

def test_generate_embeddings_saves_json(use_case, tmp_path, monkeypatch):
    # 1. Preparar a pasta "data/processed" falsa no tmp_path com um JSON de chunks simulado
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True)
    fake_chunk_file = processed_dir / "test_doc_chunks.json"
    
    fake_chunks = [
        {"chunk_id": "1", "content": "Primeiro texto simulado"},
        {"chunk_id": "2", "content": "Segundo texto simulado"}
    ]
    with open(fake_chunk_file, "w", encoding="utf-8") as f:
        json.dump(fake_chunks, f)

    # 2. Mockar o Path no use_case para salvar em tmp_path / "data" / "embeddings"
    original_path = pathlib.Path
    def mock_path(*args, **kwargs):
        if args and args[0] == "data/embeddings":
            return tmp_path / "data" / "embeddings"
        return original_path(*args, **kwargs)

    monkeypatch.setattr("modules.embedding.application.use_cases.embedding_convert.Path", mock_path)

    # 3. Executar o caso de uso passando o arquivo falso
    output_file_path = use_case.execute(str(fake_chunk_file))

    # 4. Asserções
    assert output_file_path != ""
    assert os.path.exists(output_file_path)
    
    with open(output_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Verifica se os vetores foram mesclados aos chunks
    assert isinstance(data, list)
    assert len(data) == 2
    assert "embedding" in data[0]
    assert data[0]["embedding"] == [0.99, 0.99]
    assert data[1]["embedding"] == [0.99, 0.99]
    assert data[0]["content"] == "Primeiro texto simulado"
