from modules.documents.domain.entities.document import Document


class ChunkDocumentUseCase:

    def execute(self, document: Document) -> list[str]:
        text = document.content

        if self._is_law_document(text):
            return self._split_by_articles(text)

        return self._split_by_size(text)

    def _is_law_document(self, text: str) -> bool:
        return "Art. 1" in text or "Art. 1º" in text

    def _split_by_size(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> list[str]:
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += chunk_size - overlap

        return chunks

    def _split_by_articles(self, text: str) -> list[str]:
        import re

        articles = re.split(r"(?=Art\. \d+)", text)

        return [
            article.strip()
            for article in articles
            if article.strip()
        ]