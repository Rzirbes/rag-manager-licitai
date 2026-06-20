from modules.embedding.infra.providers.sentence_transformer_provider import SentenceTransformerProvider
from modules.embedding.application.use_cases.embedding_convert import GenerateEmbeddingsUseCase
import json

provider = SentenceTransformerProvider()
use_case = GenerateEmbeddingsUseCase(provider)

file_path = 'data/processed/Edital-PE-Modelo.pdf_chunks.json'

output = use_case.execute(file_path)

with open(output, 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f"Primeiro chunk embedding length: {len(data[0]['embedding'])}")
    print(f"Primeiro valor do vetor: {data[0]['embedding'][0]}")
