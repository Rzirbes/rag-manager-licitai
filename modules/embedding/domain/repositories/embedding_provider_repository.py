from abc import ABC, abstractmethod

class EmbeddingProviderRepository(ABC):

    @abstractmethod
    def generate_embedding(self, text: str) -> list[float]:
        """
        Gera o vetor
        """
        pass

    @abstractmethod
    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Gera vetores para uma lista de textos de uma vez.
        """
        pass
