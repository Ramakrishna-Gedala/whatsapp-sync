"""
WhatsApp text export parser.

Supports export formats:
- 24-hour (Android/real export): "16/01/26, 19:46 - Sender: message"
- 12-hour AM/PM (Android):       "12/31/23, 10:30 AM - Sender: message"
- iOS:                           "[31/12/23, 10:30:45 AM] Sender: message"
"""
import re
from .base import IFileParser, FileParseResult, ParsedMessage


class WhatsAppTextFileParser(IFileParser):

    # 24-hour format: "16/01/26, 19:46 - Sender: message" (primary — real exports)
    PATTERN_24H = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*([^:]+):\s*(.+)$'
    )
    # 12-hour AM/PM (Android): "12/31/23, 10:30 AM - Sender: message"
    ANDROID_PATTERN = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}(?::\d{2})?\s*[AP]M)\s*-\s*([^:]+):\s*(.+)$'
    )
    # iOS: "[31/12/23, 10:30:45 AM] Sender: message"
    IOS_PATTERN = re.compile(
        r'^\[(\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}(?::\d{2})?\s*[AP]M)\]\s*([^:]+):\s*(.+)$'
    )
    # Timestamp-only system messages (no "Sender:" part) — drop these
    TIMESTAMP_LINE = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\s*-\s*.+$'
    )

    SKIP_PATTERNS = [
        re.compile(r'<Media omitted>', re.IGNORECASE),
        re.compile(r'Messages and calls are end-to-end encrypted', re.IGNORECASE),
        re.compile(r'^\u200e'),
        re.compile(r'This message was deleted', re.IGNORECASE),
        re.compile(r'image omitted', re.IGNORECASE),
        re.compile(r'video omitted', re.IGNORECASE),
        re.compile(r'audio omitted', re.IGNORECASE),
        re.compile(r'document omitted', re.IGNORECASE),
        re.compile(r'sticker omitted', re.IGNORECASE),
        re.compile(r'^\s*null\s*$', re.IGNORECASE),
        re.compile(r'\(file attached\)', re.IGNORECASE),
        re.compile(r'Meta AI', re.IGNORECASE),
    ]

    # Suffixes to strip from content (not skip the whole message)
    STRIP_PATTERNS = [
        re.compile(r'\s*<This message was edited>\s*$', re.IGNORECASE),
    ]

    @property
    def supported_mime_types(self) -> list[str]:
        return ['text/plain', 'text/txt', 'application/octet-stream']

    @property
    def max_file_size_bytes(self) -> int:
        return 10 * 1024 * 1024  # 10 MB

    async def parse(self, file_bytes: bytes, file_name: str) -> FileParseResult:
        errors: list[str] = []

        try:
            text = file_bytes.decode('utf-8', errors='replace')
        except Exception as e:
            return FileParseResult(
                messages=[],
                total_found=0,
                file_name=file_name,
                file_type='text/plain',
                parse_errors=[f"Failed to decode file: {e}"],
            )

        lines = text.splitlines()
        messages: list[ParsedMessage] = []
        current: ParsedMessage | None = None
        index = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            matched = self._match_line(line)

            if matched:
                # Flush previous message
                if current and self._is_valid(current.content):
                    messages.append(current)
                    index += 1

                ts, sender, content = matched
                content = self._clean_content(content)

                if self._should_skip(content) or self._should_skip(sender):
                    current = None
                    continue

                current = ParsedMessage(
                    content=content.strip(),
                    sender_name=sender.strip(),
                    timestamp_str=ts.strip(),
                    sequence_index=index,
                )
            elif self.TIMESTAMP_LINE.match(line):
                # System message (e.g. "group created", "added", "left") — flush and skip
                if current and self._is_valid(current.content):
                    messages.append(current)
                    index += 1
                current = None
            else:
                # Continuation line — append to current message
                if current and not self._should_skip(line):
                    current.content += f"\n{line}"

        # Flush final message
        if current and self._is_valid(current.content):
            messages.append(current)

        return FileParseResult(
            messages=messages,
            total_found=len(messages),
            file_name=file_name,
            file_type='text/plain',
            parse_errors=errors,
        )

    def _match_line(self, line: str) -> tuple[str, str, str] | None:
        for pattern in (self.PATTERN_24H, self.ANDROID_PATTERN, self.IOS_PATTERN):
            m = pattern.match(line)
            if m:
                return m.group(1), m.group(2), m.group(3)
        return None

    def _should_skip(self, text: str) -> bool:
        return any(p.search(text) for p in self.SKIP_PATTERNS)

    def _clean_content(self, content: str) -> str:
        for pattern in self.STRIP_PATTERNS:
            content = pattern.sub('', content)
        return content

    def _is_valid(self, content: str) -> bool:
        return bool(content and len(content.strip()) > 2)
