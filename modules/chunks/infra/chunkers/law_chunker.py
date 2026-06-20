# modules/chunks/infra/chunkers/law_chunker.py

import re
from uuid import uuid4

from modules.documents.domain.entities.document import Document
from modules.chunks.domain.entities.document_chunk import DocumentChunk
from modules.chunks.domain.chunkers.base_chunker import BaseChunker
from modules.chunks.domain.services.token_count_service import TokenCountService


MAX_ARTICLE_TOKENS = 250


class LawChunker(BaseChunker):

    def chunk(self, document: Document) -> list[DocumentChunk]:
        text = self._clean_text(document.text)
        article_blocks = self._split_by_articles_with_structure(text)

        chunks: list[DocumentChunk] = []
        chunk_index = 0

        for article_data in article_blocks:
            article_text = article_data["content"]
            article_number = self._extract_article_number(article_text)

            article_parts = self._split_large_article(article_text)

            for part_index, part_content in enumerate(article_parts, start=1):
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
                            "section_type": "article"
                            if len(article_parts) == 1
                            else "article_part",
                            "article": article_number,
                            "article_part": part_index
                            if len(article_parts) > 1
                            else None,
                            "title": article_data.get("title"),
                            "chapter": article_data.get("chapter"),
                            "section": article_data.get("section"),
                            **document.metadata,
                        },
                    )
                )

                chunk_index += 1

        return chunks

    def _split_by_articles_with_structure(self, text: str) -> list[dict[str, str | None]]:
        lines = text.splitlines()
        waiting_chapter_name = False
        current_title: str | None = None
        current_chapter: str | None = None
        current_section: str | None = None

        articles: list[dict[str, str | None]] = []
        current_article_lines: list[str] = []
        current_article_structure: dict[str, str | None] = {}

        for line in lines:
            line = line.strip()

            if not line:
                continue

            if self._is_title(line):
                current_title = line
                continue

            if self._is_chapter(line):
                current_chapter = line
                waiting_chapter_name = True
                continue

            if waiting_chapter_name:
                current_chapter = f"{current_chapter} - {line}"
                waiting_chapter_name = False
                continue

            if self._is_section(line):
                current_section = line
                continue

            if self._is_article_start(line):
                if current_article_lines:
                    articles.append(
                        {
                            "content": "\n".join(current_article_lines).strip(),
                            **current_article_structure,
                        }
                    )

                current_article_lines = [line]
                current_article_structure = {
                    "title": current_title,
                    "chapter": current_chapter,
                    "section": current_section,
                }

                continue

            if current_article_lines:
                current_article_lines.append(line)

        if current_article_lines:
            articles.append(
                {
                    "content": "\n".join(current_article_lines).strip(),
                    **current_article_structure,
                }
            )

        return articles

    def _split_large_article(self, article_text: str) -> list[str]:
        token_service = TokenCountService()

        if token_service.count_tokens(article_text) <= MAX_ARTICLE_TOKENS:
            return [article_text]

        header = self._extract_article_header(article_text)

        blocks = re.split(
            r"(?=^\s*(?:[IVXLCDM]+|§\s*\d+º?)\s*[-–])",
            article_text,
            flags=re.MULTILINE,
        )

        parts: list[str] = []
        current_part = ""

        for block in blocks:
            block = block.strip()

            if not block:
                continue

            if token_service.count_tokens(current_part + "\n" + block) > MAX_ARTICLE_TOKENS:
                if current_part:
                    parts.append(current_part.strip())
                    current_part = block
                else:
                    sub_pieces = token_service.split_text_by_tokens(block, max_tokens=MAX_ARTICLE_TOKENS)
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

    def _extract_article_header(self, text: str) -> str | None:
        lines = text.splitlines()

        if not lines:
            return None

        first_line = lines[0].strip()

        if self._is_article_start(first_line):
            return first_line

        return None

    def _extract_article_number(self, text: str) -> str | None:
        match = re.search(r"Art\.?\s+(\d+)[º°]?", text)

        if not match:
            return None

        return match.group(1)

    def _is_article_start(self, line: str) -> bool:
        return bool(re.match(r"^Art\.?\s+\d+[º°]?", line))

    def _is_title(self, line: str) -> bool:
        return bool(re.match(r"^TÍTULO\s+[IVXLCDM]+", line, re.IGNORECASE))

    def _is_chapter(self, line: str) -> bool:
        return bool(re.match(r"^CAPÍTULO\s+[IVXLCDM]+", line, re.IGNORECASE))

    def _is_section(self, line: str) -> bool:
        return bool(re.match(r"^SEÇÃO\s+[IVXLCDM]+", line, re.IGNORECASE))

    def _clean_text(self, text: str) -> str:
        lines = text.splitlines()

        ignored_patterns = [
            r"REPÚBLICA FEDERATIVA DO BRASIL",
            r"IMPRENSA NACIONAL",
            r"ISSN",
            r"Documento assinado digitalmente",
            r"www\.in\.gov\.br",
            r"Esta edição completa do DOU",
            r"Sumário",
            r"Atos do Poder Legislativo",
            r"Presidência da República",
            r"Ministério da Educação",
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