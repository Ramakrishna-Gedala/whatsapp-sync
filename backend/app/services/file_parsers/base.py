from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ParsedMessage:
    """A single message extracted from a file."""
    content: str
    sender_name: str | None = None
    timestamp_str: str | None = None
    sequence_index: int = 0


@dataclass
class FileParseResult:
    """Result of parsing an entire uploaded file."""
    messages: list[ParsedMessage]
    total_found: int
    file_name: str
    file_type: str
    parse_errors: list[str] = field(default_factory=list)


class IFileParser(ABC):
    """
    Abstract interface for all file parsers.
    To add a new file type: subclass this, implement parse(),
    register in FileParserFactory. No other changes needed.
    """

    @abstractmethod
    async def parse(self, file_bytes: bytes, file_name: str) -> FileParseResult:
        """Parse file bytes into a list of ParsedMessages. Must be async."""
        ...

    @property
    @abstractmethod
    def supported_mime_types(self) -> list[str]:
        """MIME types this parser handles."""
        ...

    @property
    @abstractmethod
    def max_file_size_bytes(self) -> int:
        """Maximum file size this parser accepts."""
        ...
