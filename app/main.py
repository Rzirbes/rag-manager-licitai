from modules.documents.application.use_cases.extract_document_text import (
    ExtractDocumentTextUseCase,
)

from modules.chunks.application.use_cases.chunk_document import (
    ChunkDocumentUseCase,
)

from modules.documents.infra.extractors.smart_document_extractor import (
    SmartDocumentExtractor,
)


extractor = SmartDocumentExtractor()

extract_use_case = ExtractDocumentTextUseCase(
    extractor
)

chunk_use_case = ChunkDocumentUseCase()

document = extract_use_case.execute(
    "data/raw/INPDFViewer.pdf"
)

chunks = chunk_use_case.execute(
    document
)

print(f"Chunks gerados: {len(chunks)}")

for index, chunk in enumerate(chunks, start=1):
    print("=" * 80)
    print(f"CHUNK {index}")
    print("=" * 80)
    print(f"ID: {chunk.chunk_id}")
    print(f"Documento: {chunk.document_id}")
    print(f"Índice: {chunk.chunk_index}")
    print(f"Tipo: {chunk.metadata.get('document_type')}")
    print(f"Arquivo: {chunk.metadata.get('file_name')}")
    print(f"Tamanho: {len(chunk.content)} caracteres")
    print(chunk.content[:500])
    print()