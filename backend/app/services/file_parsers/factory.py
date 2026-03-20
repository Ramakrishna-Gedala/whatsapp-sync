"""
FileParserFactory — maps MIME type → parser instance.

Open/Closed: adding a new file type requires ONLY:
  1. Create a new IFileParser subclass
  2. Call FileParserFactory.register(YourParser)
  Zero changes to anything else.
"""
from .base import IFileParser
from .text_parser import WhatsAppTextFileParser


class FileParserFactory:
    _registry: dict[str, type[IFileParser]] = {}

    @classmethod
    def register(cls, parser_class: type[IFileParser]) -> None:
        instance = parser_class()
        for mime_type in instance.supported_mime_types:
            cls._registry[mime_type] = parser_class

    @classmethod
    def get_parser(cls, mime_type: str) -> IFileParser | None:
        klass = cls._registry.get(mime_type)
        return klass() if klass else None

    @classmethod
    def supported_types(cls) -> list[str]:
        return list(cls._registry.keys())


# ── Register parsers ────────────────────────────────────────
FileParserFactory.register(WhatsAppTextFileParser)

# FUTURE — uncomment when implementing:
# from .pdf_parser import PdfFileParser
# FileParserFactory.register(PdfFileParser)
# from .voice_parser import VoiceFileParser
# FileParserFactory.register(VoiceFileParser)
# from .image_parser import ImageFileParser
# FileParserFactory.register(ImageFileParser)
