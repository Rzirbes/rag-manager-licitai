# modules/embedding/infra/vector_dbs/chroma_vector_db.py
import os
import chromadb
from chromadb.config import Settings
from modules.embedding.domain.repositories.vector_db_repository import VectorDbRepository

class ChromaVectorDb(VectorDbRepository):
    def __init__(self, db_path: str = "data/chroma_db"):
       
        os.makedirs(db_path, exist_ok=True)
        
        # Conecta ao PersistentClient do Chroma
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )

    def upsert_chunks(self, collection_name: str, chunks: list[dict], embeddings: list[list[float]]):
       
        if not chunks or not embeddings:
            return

        # Busca ou cria a coleção 
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"} 
        )

        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        
        # Prepara os metadados (garante que tudo seja str, int, float, bool. Dicionários aninhados não são aceitos)
        metadatas = []
        for chunk in chunks:
            # Pega o 'metadata' do chunk e adiciona algumas chaves externas
            meta = chunk.get("metadata", {}).copy()
            meta["document_id"] = chunk["document_id"]
            meta["chunk_index"] = chunk["chunk_index"]
            
            # Limpa valores nulos complexos que o Chroma não aceita
            clean_meta = {}
            for k, v in meta.items():
                if v is not None:
                    if isinstance(v, (str, int, float, bool)):
                        clean_meta[k] = v
                    else:
                        clean_meta[k] = str(v)
            metadatas.append(clean_meta)

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, collection_name: str, query_embeddings: list[list[float]], n_results: int = 5) -> list[dict]:
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            print(f"Coleção {collection_name} não encontrada.")
            return []

        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )

        formatted_results = []
        # O Chroma retorna listas de listas (uma pra cada query). Como geralmente mandamos 1 query por vez,
        # vamos pegar o índice 0. Se houver mais, iteramos normalmente.
        
        for q_idx in range(len(query_embeddings)):
            q_results = []
            
            # Verificamos se há resultados para esta query
            if not results["ids"] or not results["ids"][q_idx]:
                continue
                
            for i in range(len(results["ids"][q_idx])):
                match = {
                    "id": results["ids"][q_idx][i],
                    "document": results["documents"][q_idx][i] if results["documents"] else None,
                    "metadata": results["metadatas"][q_idx][i] if results["metadatas"] else {},
                    "distance": results["distances"][q_idx][i] if results["distances"] else None
                }
                q_results.append(match)
            formatted_results.append(q_results)
            
        # Retorna a lista achatada se for só uma query, pra facilitar
        if len(query_embeddings) == 1 and formatted_results:
            return formatted_results[0]
            
        return formatted_results
