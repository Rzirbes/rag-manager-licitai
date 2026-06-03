# modules/documents/domain/entities/document.py

from dataclasses import dataclass
from collections.abc import Mapping
from typing import Any
import datetime


@dataclass
class Document:
    # A entidade deve armazenar data de upload
    created_at: datetime.datetime
    
    updated_at: datetime.datetime

    document_id: str

    file_name: str

    document_type: str

    source_path: str

    text: str

    metadata: Mapping[str, Any]