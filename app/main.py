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


extractor = SmartDocumentExtractor()

extract_use_case = ExtractDocumentTextUseCase(
    extractor
)

chunk_use_case = ChunkDocumentUseCase()

document = extract_use_case.execute(
    'data/raw/test-word-document.docx' 
    #'data/raw/Edital-PE-Modelo.pdf'
    #'data/raw/INPDFViewer.pdfr' # apenas teste de para ver o tratamento de erro caso esteja corrompido ou vazio
    #'data/raw/INPDFViewer.pdf'
    #'data/raw/Nova_Engenharia_das_Contratações.pdf' # nenhum de nossos extratores conseguiu extrair os dados de um slide convertido em pdf
    #'data/raw/test-csv-document.csv'
    #'data/raw/test-xlsx-document.xlsx'
    #'data/raw/test-odt-document.odt'
)

chunks = chunk_use_case.execute(
    document
)

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