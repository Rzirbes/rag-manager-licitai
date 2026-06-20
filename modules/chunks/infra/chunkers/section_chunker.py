# modules/chunks/infra/chunkers/section_chunker.py

import re
from uuid import uuid4

from modules.documents.domain.entities.document import Document
from modules.chunks.domain.entities.document_chunk import DocumentChunk
from modules.chunks.domain.chunkers.base_chunker import BaseChunker
from modules.chunks.domain.services.token_count_service import TokenCountService


MAX_SECTION_TOKENS = 250


class SectionChunker(BaseChunker):

    def chunk(self, document: Document) -> list[DocumentChunk]:
        text = self._clean_text(document.text)
        sections = self._split_by_sections(text)

        if not sections:
            return []

        chunks: list[DocumentChunk] = []
        chunk_index = 0

        for section_data in sections:
            section_text = section_data["content"]
            section_parts = self._split_large_section(section_text)

            for part_index, part_content in enumerate(section_parts, start=1):
                chunks.append(
                    DocumentChunk(
                        document_id=document.document_id,
                        chunk_id=str(uuid4()),
                        content=part_content.strip(),
                        chunk_index=chunk_index,
                        metadata={
                            "file_name": document.file_name,
                            "document_type": document.document_type,
                            "source_path": document.source_path,
                            "section_type": section_data["section_type"]
                            if len(section_parts) == 1
                            else f'{section_data["section_type"]}_part',
                            "section_title": section_data["title"],
                            "section_number": section_data["number"],
                            "section_part": part_index if len(section_parts) > 1 else None,
                            "processed_at": document.metadata.get("processed_at"),
                            "document_size": document.metadata.get("document_size"),
                            "file_size_bytes": document.metadata.get("file_size_bytes"),
                            "page_count": document.metadata.get("page_count"),
                        },
                    )
                )

                chunk_index += 1

        return chunks

    def _split_by_sections(self, text: str) -> list[dict[str, str | None]]:
        lines = text.splitlines()

        sections: list[dict[str, str | None]] = []
        current_lines: list[str] = []
        current_title: str | None = None
        current_number: str | None = None
        current_type: str = "section"

        for line in lines:
            line = line.strip()

            if not line:
                continue

            header = self._detect_section_header(line)

            if header:
                if current_lines:
                    sections.append(
                        {
                            "content": "\n".join(current_lines).strip(),
                            "title": current_title,
                            "number": current_number,
                            "section_type": current_type,
                        }
                    )

                current_lines = [line]
                current_title = header["title"]
                current_number = header["number"]
                current_type = header["section_type"]
                continue

            # antes só adicionava se current_lines já existisse
            # agora guarda texto mesmo antes de detectar seção
            current_lines.append(line)

        if current_lines:
            sections.append(
                {
                    "content": "\n".join(current_lines).strip(),
                    "title": current_title,
                    "number": current_number,
                    "section_type": current_type,
                }
            )

        return sections

    def _detect_section_header(self, line: str) -> dict[str, str | None] | None:
        clause_match = re.match(
            r"^(CL[ÁA]USULA\s+[A-ZÀ-Ú\s]+)\s*[-–]\s*(.+)$",
            line,
)       

        if clause_match:
            return {
                "section_type": "clause",
                "number": clause_match.group(1),
                "title": line,
            }

        numbered_section_match = re.match(
            r"^(\d+)\.\s+([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9][A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9\s,./ºª()\-–]+)$",
            line,
        )

        if numbered_section_match:
            return {
                "section_type": "numbered_section",
                "number": numbered_section_match.group(1),
                "title": line,
            }

        declaration_item_match = re.match(
            r"^(\d+)\.\s*\(\s*\)\s+(.+)$",
            line,
            flags=re.IGNORECASE,
        )

        if declaration_item_match:
            return {
                "section_type": "declaration_item",
                "number": declaration_item_match.group(1),
                "title": line[:120],
            }

        return None

    def _split_large_section(self, section_text: str) -> list[str]:
        token_service = TokenCountService()

        if token_service.count_tokens(section_text) <= MAX_SECTION_TOKENS:
            return [section_text]

        header = self._extract_section_header(section_text)

        blocks = re.split(
            r"(?=^\s*(?:\d+\.\d+\.?|\d+\.\d+\.\d+\.?|[a-z]\))\s*)",
            section_text,
            flags=re.MULTILINE,
        )

        parts: list[str] = []
        current_part = ""

        for block in blocks:
            block = block.strip()

            if not block:
                continue

            # Testa se adicionar o bloco estoura o limite de tokens
            if token_service.count_tokens(current_part + "\n" + block) > MAX_SECTION_TOKENS:
                if current_part:
                    parts.append(current_part.strip())
                    current_part = block
                else:
                    # Se só o bloco sozinho já é maior que o limite, forçamos o particionamento duro dele
                    sub_pieces = token_service.split_text_by_tokens(block, max_tokens=MAX_SECTION_TOKENS)
                    for sp in sub_pieces[:-1]:
                        parts.append(sp)
                    current_part = sub_pieces[-1]
            else:
                current_part += "\n" + block if current_part else block

        if current_part:
            parts.append(current_part.strip())

        if len(parts) <= 1 or not header:
            return parts

        normalized_parts = []

        for index, part in enumerate(parts):
            if index == 0:
                normalized_parts.append(part)
                continue

            normalized_parts.append(f"{header}\n\n{part}")

        return normalized_parts

    def _extract_section_header(self, text: str) -> str | None:
        lines = text.splitlines()

        if not lines:
            return None

        return lines[0].strip()

    def _clean_text(self, text: str) -> str:
        lines = text.splitlines()

        ignored_patterns = [
            r"ESTADO DO RIO GRANDE DO SUL",
            r"PREFEITURA MUNICIPAL DE ARROIO DO SAL",
            r"SECRETARIA DE ADMINISTRAÇÃO",
            r"SETOR DE LICITAÇÕES",
            r"Rua Alegrete",
            r"Visite o nosso site",
            r"E-mail:",
            r"Página\s+\d+\s+de\s+\d+",
            r"Pregão Eletrônico:\s*\d+",
            r"Concorrência Eletrônica:\s*\d+",
            r"Processo Administrativo:",
            r"^\d+$",
        ]

        cleaned_lines = []

        for line in lines:
            line = line.strip()

            if not line:
                continue

            should_ignore = any(
                re.search(pattern, line, re.IGNORECASE)
                for pattern in ignored_patterns
            )

            if should_ignore:
                continue

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)