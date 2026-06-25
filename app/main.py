from modules.chunks.domain.entities.document_chunk import DocumentChunk
from modules.documents.domain.entities.document import Document
from modules.documents.application.use_cases.extract_document_text import (
    ExtractDocumentTextUseCase,
)

from modules.chunks.application.use_cases.chunk_document import (
    ChunkDocumentUseCase,
)

from modules.documents.infra.extractors.smart_document_extractor import (
    SmartDocumentExtractor,
)

from modules.embedding.infra.providers.sentence_transformer_provider import (
    SentenceTransformerProvider,
)
from modules.embedding.application.use_cases.embedding_convert import (
    GenerateEmbeddingsUseCase,
)
from modules.embedding.infra.vector_dbs.chroma_vector_db import (
    ChromaVectorDb,
)


extractor = SmartDocumentExtractor()

extract_use_case = ExtractDocumentTextUseCase(
    extractor
)

chunk_use_case = ChunkDocumentUseCase()

embedding_provider = SentenceTransformerProvider()
vector_db = ChromaVectorDb()
embedding_use_case = GenerateEmbeddingsUseCase(embedding_provider, vector_db)

from modules.documents.application.exceptions import DocumentExtractionError

arquivo_alvo = None

'''
Implementei esta mecanica pra ver os tratamentos de erros
pois como tava retornando typerror e não passando pelas validações try catch 
resolvi melhorar pra ficar mais facil de ver os tratamentos de erros
Ai é só descomentar o arquivo que deseja testar
'''
arquivo_alvo = 'data/raw/Edital-CREDENCIAMENTO-Modelo.pdf' # ver se passa na validação de erro
#arquivo_alvo = 'data/raw/test_invalid_format.docx'

if not arquivo_alvo:
    print("Erro: Faltando documentos para extrair. Por favor, defina um arquivo alvo.")
    exit(1)

from pathlib import Path

try:
    print(f"Extraindo texto de {arquivo_alvo}...")
    document = extract_use_case.execute(arquivo_alvo)
    
    print("Fatiando o documento (chunking)...")
    chunks = chunk_use_case.execute(document)
    

    chunk_json_path = f"data/processed/{Path(document.file_name).stem}_chunks.json"
    
    print("Gerando os embeddings matemáticos...")
    output_embedded_file = embedding_use_case.execute(chunk_json_path)
    
except DocumentExtractionError as e:
    print(e)
    exit(1)

def print_sizes(document: Document, chunks: list[DocumentChunk]) -> None:
    print(f"O tamanho do documento é de {document.metadata.get('document_size')} caracteres")
    print(f"O tamanho do arquivo é de {document.metadata.get('file_size_bytes')} bytes")
    print(f"Quantidade de páginas: {document.metadata.get('page_count')}")

    print(f"Chunks gerados: {len(chunks)}")
    print()

def print_chunk(chunk, index: int):
    document_type = chunk.metadata.get("document_type")

    print("=" * 80)
    print(f"CHUNK {index}")
    print("=" * 80)
    print(f"ID: {chunk.chunk_id}")
    print(f"Documento: {chunk.document_id}")
    print(f"Índice: {chunk.chunk_index}")
    print(f"Tipo do documento: {document_type}")
    print(f"Arquivo: {chunk.metadata.get('file_name')}")
    print(f"Tamanho do Documento Original: {chunk.metadata.get('document_size')} caracteres / {chunk.metadata.get('page_count')} páginas")
    print(f"Tamanho do Chunk: {len(chunk.content)} caracteres")

    if document_type == "law":
        print(f"Tipo da seção: {chunk.metadata.get('section_type')}")
        print(f"Título: {chunk.metadata.get('title')}")
        print(f"Capítulo: {chunk.metadata.get('chapter')}")
        print(f"Seção: {chunk.metadata.get('section')}")
        print(f"Artigo: {chunk.metadata.get('article')}")
        print(f"Parte do artigo: {chunk.metadata.get('article_part')}")

    elif document_type in [
        "bid_notice",
        "contract",
        "price_registry_minutes",
        "declaration_model",
        "addendum",
    ]:
        print(f"Tipo da seção: {chunk.metadata.get('section_type')}")
        print(f"Número da seção: {chunk.metadata.get('section_number')}")
        print(f"Título da seção: {chunk.metadata.get('section_title')}")

    else:
        print(f"Tipo da seção: {chunk.metadata.get('section_type')}")

    print(chunk.content)
    print()


print_sizes(document, chunks)

for index, chunk in enumerate(chunks, start=1):
    print_chunk(chunk, index)

print("\n" + "=" * 80)
print("TESTE DE BUSCA SEMÂNTICA NO CHROMADB (RETRIEVAL)")
print("=" * 80)

# Altere este texto para testar a busca matemática no banco
# lembre de checar qual arquivo e teste se as perguntas fazem sentido pro arquivo

query_text = "Quais as regras para a manutenção de roçadeiras?"
print(f"Buscando por: '{query_text}'")

# Gera o embedding da pergunta
query_vector = embedding_provider.generate_embedding(query_text)

# Consulta no Vector DB
search_results = vector_db.search(
    collection_name="documents_collection",
    query_embeddings=[query_vector],
    n_results=3
)

if search_results:
    for idx, match in enumerate(search_results, start=1):
        # A 'distance' no Chroma com 'cosine' é calculada como 1 - CosineSimilarity. 
        # Portanto, quanto mais perto de 0, mais parecido!
        print(f"\n[{idx}] (Distância: {match['distance']:.4f})")
        print(f"Documento (trecho): {match['document'][:200]}...")
        print(f"Metadados: Título={match['metadata'].get('title', 'N/A')}")
else:
    print("Nenhum resultado encontrado.")

