from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator


@dataclass
class EmailRecord:
    email_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    source_path: str = ""
    source_row: int = -1


@dataclass
class SchemaInspection:
    path: str
    row_count: int | None
    columns: list[str]
    inferred_text_column: str | None
    inferred_metadata_columns: list[str]
    complete: bool
    notes: list[str] = field(default_factory=list)


class DatasetAdapter(ABC):
    @abstractmethod
    def load(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def inspect_schema(self) -> list[SchemaInspection]:
        raise NotImplementedError

    @abstractmethod
    def iter_records(self) -> Iterator[EmailRecord]:
        raise NotImplementedError

    @abstractmethod
    def normalize_record(self, raw: dict[str, Any], source_path: str, source_row: int) -> EmailRecord:
        raise NotImplementedError
