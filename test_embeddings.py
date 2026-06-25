from modules.embedding.infra.providers.sentence_transformer_provider import SentenceTransformerProvider
from modules.embedding.application.use_cases.embedding_convert import GenerateEmbeddingsUseCase
from modules.embedding.infra.vector_dbs.chroma_vector_db import ChromaVectorDb
import json

if __name__ == "__main__":
    provider = SentenceTransformerProvider()
    vector_db = ChromaVectorDb()
    use_case = GenerateEmbeddingsUseCase(provider, vector_db)

    file_path = 'data/processed/Edital-PE-Modelo.pdf_chunks.json'

    try:
        output = use_case.execute(file_path)

        with open(output, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Primeiro chunk embedding length: {len(data[0]['embedding'])}")
            print(f"Primeiro valor do vetor: {data[0]['embedding'][0]}")
    except FileNotFoundError:
        print(f"O arquivo de teste não foi encontrado: {file_path}")
