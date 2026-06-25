import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from modules.embedding.infra.providers.sentence_transformer_provider import SentenceTransformerProvider

@pytest.fixture
def mock_sentence_transformer():
    # simula a classe SentenceTransformer da biblioteca HuggingFace.
    with patch("modules.embedding.infra.providers.sentence_transformer_provider.SentenceTransformer") as mock:
        mock_instance = MagicMock()
        
        # simula o retorno de um vetor numpy para o método encode
        def fake_encode(text_or_texts, **kwargs):
            if isinstance(text_or_texts, str):
                return np.array([0.1, 0.2, 0.3])
            return np.array([[0.1, 0.2, 0.3] for _ in text_or_texts])
            
        mock_instance.encode.side_effect = fake_encode
        mock.return_value = mock_instance
        yield mock

def test_provider_initialization(mock_sentence_transformer):
    provider = SentenceTransformerProvider("fake-model")
    mock_sentence_transformer.assert_called_once_with("fake-model")

def test_generate_embedding_single(mock_sentence_transformer):
    provider = SentenceTransformerProvider("fake-model")
    vector = provider.generate_embedding("Test text")
    
    assert isinstance(vector, list)
    assert len(vector) == 3
    assert vector == [0.1, 0.2, 0.3]

def test_generate_embeddings_batch(mock_sentence_transformer):
    provider = SentenceTransformerProvider("fake-model")
    vectors = provider.generate_embeddings_batch(["Text 1", "Text 2"])
    
    assert isinstance(vectors, list)
    assert len(vectors) == 2
    assert isinstance(vectors[0], list)
    assert vectors[0] == [0.1, 0.2, 0.3]
    assert vectors[1] == [0.1, 0.2, 0.3]
