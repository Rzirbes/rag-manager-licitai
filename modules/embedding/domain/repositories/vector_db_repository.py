# modules/embedding/domain/repositories/vector_db_repository.py

from abc import ABC, abstractmethod

class VectorDbRepository(ABC):
    @abstractmethod
    def upsert_chunks(self, collection_name: str, chunks: list[dict], embeddings: list[list[float]]):
        """
        Insere ou atualiza os chunks e seus respectivos embeddings 
        """
        pass

    @abstractmethod
    def search(self, collection_name: str, query_embeddings: list[list[float]], n_results: int = 5) -> list[dict]:
        """
        Busca os N vetores mais semelhantes no banco de dados com base na query fornecida.
        """
        pass