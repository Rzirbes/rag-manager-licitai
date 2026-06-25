# modules/embedding/application/use_cases/embedding_convert.py

import json
import os
from pathlib import Path
from modules.embedding.domain.repositories.embedding_provider_repository import EmbeddingProviderRepository
from modules.embedding.domain.repositories.vector_db_repository import VectorDbRepository

class GenerateEmbeddingsUseCase:
    """
    Responsável por ler os arquivos chunks, gerar os embeddings numéricos 
    e enviá-los diretamente para o Banco Vetorial.
    Ainda mantém o backup em _embedded.json por conveniência e auditoria.
    """

    def __init__(self, provider: EmbeddingProviderRepository, vector_db: VectorDbRepository):
        self.provider = provider
        self.vector_db = vector_db

    def execute(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        if not chunks:
            print(f"[Embeddings] O arquivo {file_path} não contém chunks.")
            return ""

        print(f"[Embeddings] Iniciando vetorização de {len(chunks)} chunks do arquivo {Path(file_path).name}...")

        # Extrai apenas os textos
        texts_to_embed = [chunk["content"] for chunk in chunks]

        # Gera os embeddings matemáticos em batch 
        vectors = self.provider.generate_embeddings_batch(texts_to_embed)

        # Atualiza o banco de dados vetorial
        print(f"[Embeddings] Inserindo os dados gerados no Banco Vetorial...")
        self.vector_db.upsert_chunks(
            collection_name="documents_collection",
            chunks=chunks,
            embeddings=vectors
        )

        # Injeta os vetores de volta no dicionário para backup
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = vectors[i]

        # Mantém o backup na camada (data/embeddings)
        embeddings_dir = Path("data/embeddings")
        embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = Path(file_path).name.replace("_chunks.json", "")
        if base_name.endswith(".json"):
            base_name = base_name.replace(".json", "")
            
        output_path = embeddings_dir / f"{base_name}_embedded.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=4)

        print(f"[Embeddings] Processo concluído! Vetores salvos no DB e backup em: {output_path}")
        return str(output_path)
