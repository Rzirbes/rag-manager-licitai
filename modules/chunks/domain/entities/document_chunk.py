# modules/chunks/domain/entities/document_chunk.py

from dataclasses import dataclass
from collections.abc import Mapping
from typing import Any


@dataclass
class DocumentChunk:
    document_id: str
    chunk_id: str

    content: str

    chunk_index: int

    metadata: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "metadata": dict(self.metadata),
        }