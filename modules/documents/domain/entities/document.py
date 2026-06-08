# modules/documents/domain/entities/document.py

from dataclasses import dataclass
from collections.abc import Mapping
from typing import Any


@dataclass
class Document:
    document_id: str

    file_name: str

    document_type: str

    source_path: str

    text: str
    # armazenar

    metadata: Mapping[str, Any]