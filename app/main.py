from modules.documents.application.use_cases.extract_document_text import (
    ExtractDocumentTextUseCase,
)

from modules.documents.application.use_cases.chunk_document import (
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