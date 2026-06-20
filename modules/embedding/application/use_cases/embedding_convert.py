import json
import os
from pathlib import Path
from modules.embedding.domain.repositories.embedding_provider_repository import EmbeddingProviderRepository

class GenerateEmbeddingsUseCase:
    """
    responsável por ler os arquivos chunks
    da camada processed, gerar os embeddings e exportar para data/embeddings.
    Como ainda não estamos usando um Vector DB, vamos salvar como JSON.
    """

    def __init__(self, provider: EmbeddingProviderRepository):
        self.provider = provider

    def execute(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        if not chunks:
            print(f"[Embeddings] O arquivo {file_path} não contém chunks.")
            return ""

        print(f"[Embeddings] Iniciando vetorização de {len(chunks)} chunks do arquivo {Path(file_path).name}...")

        # extrai apenas os textos
        texts_to_embed = [chunk["content"] for chunk in chunks]

        # gera os embeddings em batch 
        vectors = self.provider.generate_embeddings_batch(texts_to_embed)

        # injeta os vetores de volta no dicionário
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = vectors[i]

        # salva na nova camada (data/embeddings)
        embeddings_dir = Path("data/embeddings")
        embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        # O nome do arquivo original é algo como "Edital-PE-Modelo.pdf_chunks.json"
        # remove o _chunks.json se existir e coloca _embedded.json para não dar confusão
        base_name = Path(file_path).name.replace("_chunks.json", "")
        if base_name.endswith(".json"):
            base_name = base_name.replace(".json", "")
            
        output_path = embeddings_dir / f"{base_name}_embedded.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=4)

        print(f"[Embeddings] Vetorização concluída! Salvo em: {output_path}")
        return str(output_path)
