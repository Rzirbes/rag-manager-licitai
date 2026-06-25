from sentence_transformers import SentenceTransformer
from modules.embedding.domain.repositories.embedding_provider_repository import EmbeddingProviderRepository

class SentenceTransformerProvider(EmbeddingProviderRepository):
    """
    Provedor local de embeddings usando HuggingFace sentence-transformers.
    Modelo padrão: all-MiniLM-L6-v2, leve e rápido
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text: str) -> list[float]:
        vector = self.model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()
