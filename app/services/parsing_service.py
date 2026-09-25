from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError


@dataclass(frozen=True)
class ParsedPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class ParsedPdf:
    pages: list[ParsedPage]
    total_pages: int


def parse_txt(filename: str, file_bytes: bytes) -> str:
    if Path(filename).suffix.lower() != ".txt":
        raise ValueError("file must have a .txt extension")

    try:
        text = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("the text file must use UTF-8 encoding") from error

    text = text.strip()
    if not text:
        raise ValueError("the text file is empty")

    return text


def parse_pdf(filename: str, file_bytes: bytes) -> ParsedPdf:
    if Path(filename).suffix.lower() != ".pdf":
        raise ValueError("file must have a .pdf extension")

    try:
        reader = PdfReader(BytesIO(file_bytes))
    except PdfReadError as error:
        raise ValueError("the PDF file is invalid") from error

    if reader.is_encrypted:
        try:
            unlocked = reader.decrypt("")
        except Exception as error:
            raise ValueError(
                "encrypted PDF files are not supported"
            ) from error
        if not unlocked:
            raise ValueError("encrypted PDF files are not supported")

    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(ParsedPage(page_number=page_number, text=text))

    if not pages:
        raise ValueError(
            "no text was found; scanned PDFs require OCR"
        )

    return ParsedPdf(pages=pages, total_pages=len(reader.pages))
