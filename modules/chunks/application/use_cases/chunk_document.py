# modules/chunks/application/use_cases/chunk_document.py

from pathlib import Path
from uuid import uuid4
import json

from modules.documents.domain.entities.document import Document
from modules.chunks.domain.entities.document_chunk import DocumentChunk

from modules.chunks.infra.chunkers.generic_chunker import GenericChunker
from modules.chunks.infra.chunkers.law_chunker import LawChunker
from modules.chunks.infra.chunkers.section_chunker import SectionChunker


class ChunkDocumentUseCase:

    def __init__(self):
        self.generic_chunker = GenericChunker()
        self.law_chunker = LawChunker()
        self.section_chunker = SectionChunker()

    def detect_document_type(self, text: str, file_name: str = "") -> str:
        upper_text = text.upper()
        upper_file = file_name.upper()

        if "MINUTA-DE-CONTRATO" in upper_file or "MINUTA DE CONTRATO" in upper_file:
            return "contract"

        if "ATA-DE-REGISTRO" in upper_file or "ATA DE REGISTRO" in upper_file:
            return "price_registry_minutes"

        if "DECLARA" in upper_file:
            return "declaration_model"

        if "REEQUIL" in upper_file or "RENOVA" in upper_file:
            return "addendum"

        if "ART. 1º" in upper_text or "LEI Nº" in upper_text:
            return "law"

        if "CONTRATO N.º" in upper_text or "CONTRATO Nº" in upper_text:
            return "contract"

        if "ATA DE REGISTRO DE PREÇOS" in upper_text:
            return "price_registry_minutes"

        if "MODELO DE DECLARAÇÃO" in upper_text:
            return "declaration_model"

        if "ADITIVO" in upper_text:
            return "addendum"

        if (
            "EDITAL DE PREGÃO" in upper_text
            or "EDITAL DE CONCORRÊNCIA" in upper_text
            or "CHAMAMENTO PÚBLICO" in upper_text
        ):
            return "bid_notice"

        return "generic"

    def execute(self, document: Document) -> list[DocumentChunk]:
        try:
            document_type = (
                document.document_type
                if document.document_type
                else self.detect_document_type(document.text, document.file_name)
            )

            document.document_type = document_type

            if document_type == "law":
                chunks = self.law_chunker.chunk(document)

            elif document_type in [
                "bid_notice",
                "contract",
                "price_registry_minutes",
                "declaration_model",
                "addendum",
            ]:
                chunks = self.section_chunker.chunk(document)

            else:
                chunks = self.generic_chunker.chunk(document)

            if not chunks:
                print(
                    f"[Aviso] Nenhum chunk gerado com chunker especializado para "
                    f"{document_type}. Usando GenericChunker."
                )
                chunks = self.generic_chunker.chunk(document)

            table_chunks = self._create_table_chunks(
                document=document,
                start_index=len(chunks),
            )

            chunks.extend(table_chunks)

            self._save_chunks(document, chunks)

            return chunks

        except Exception as e:
            from modules.chunks.application.exceptions import DocumentChunkingError

            raise DocumentChunkingError(
                f"Erro ao fatiar (chunking) o documento {document.file_name}: {e}"
            ) from e

    def _create_table_chunks(
        self,
        document: Document,
        start_index: int = 0,
    ) -> list[DocumentChunk]:
        table_chunks: list[DocumentChunk] = []

        tables_by_page = document.metadata.get("tables", [])

        for page_data in tables_by_page:
            page = page_data.get("page")
            tables = page_data.get("tables", [])

            for table_index, table in enumerate(tables):
                content = self._table_to_text(table)

                if not content:
                    continue

                table_chunks.append(
                    DocumentChunk(
                        document_id=document.document_id,
                        chunk_id=str(uuid4()),
                        chunk_index=start_index + len(table_chunks),
                        content=content,
                        metadata={
                            "file_name": document.file_name,
                            "document_type": document.document_type,
                            "source_path": document.source_path,
                            "chunk_type": "table",
                            "page": page,
                            "table_index": table_index,
                            "processed_at": document.metadata.get("processed_at"),
                            "document_size": document.metadata.get("document_size"),
                            "file_size_bytes": document.metadata.get("file_size_bytes"),
                            "page_count": document.metadata.get("page_count"),
                        },
                    )
                )

        return table_chunks

    def _table_to_text(self, table: list[list[str | None]]) -> str:
        rows = []

        for row in table:
            cells = [
                str(cell).replace("\n", " ").strip()
                for cell in row
                if cell is not None and str(cell).strip()
            ]

            if cells:
                rows.append(" | ".join(cells))

        if not rows:
            return ""

        return "TABELA EXTRAÍDA:\n" + "\n".join(rows)

    def _save_chunks(
        self,
        document: Document,
        chunks: list[DocumentChunk],
    ) -> None:
        processed_dir = Path("data/processed")
        processed_dir.mkdir(parents=True, exist_ok=True)

        json_path = processed_dir / f"{Path(document.file_name).stem}_chunks.json"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {
                        "chunk_id": chunk.chunk_id,
                        "document_id": chunk.document_id,
                        "chunk_index": chunk.chunk_index,
                        "content": chunk.content,
                        "metadata": chunk.metadata,
                    }
                    for chunk in chunks
                ],
                f,
                ensure_ascii=False,
                indent=4,
            )