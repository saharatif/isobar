"""File-type routing, scanned-PDF detection, and edge cases."""
from io import BytesIO

import pytest

from app.config import DOCX_MIME, PDF_MIME
from app.services.parsing import (
    EmptyDocumentError,
    ScannedPDFError,
    UnsupportedFileTypeError,
    parse_resume,
)


def make_pdf(text: str | None) -> bytes:
    import pymupdf

    doc = pymupdf.open()
    page = doc.new_page()
    if text:
        page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def make_docx(paragraphs: list[str]) -> bytes:
    import docx

    document = docx.Document()
    for p in paragraphs:
        document.add_paragraph(p)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


class TestTextParsing:
    def test_plain_text_roundtrip(self):
        assert parse_resume(b"Jane Doe\nPython engineer", "text/plain") == (
            "Jane Doe\nPython engineer"
        )

    def test_markdown_accepted(self):
        assert "Jane" in parse_resume(b"# Jane Doe", "text/markdown")

    def test_invalid_utf8_does_not_crash(self):
        text = parse_resume(b"Jane \xff\xfe Doe", "text/plain")
        assert "Jane" in text

    def test_empty_text_raises(self):
        with pytest.raises(EmptyDocumentError):
            parse_resume(b"   \n  ", "text/plain")


class TestPdfParsing:
    def test_text_pdf_parses(self):
        content = make_pdf("Jane Doe, Python engineer. " * 20)
        assert "Jane Doe" in parse_resume(content, PDF_MIME)

    def test_blank_pdf_treated_as_scanned(self):
        content = make_pdf(None)
        with pytest.raises(ScannedPDFError):
            parse_resume(content, PDF_MIME)

    def test_corrupt_pdf_raises_parsing_error(self):
        from app.services.parsing import ParsingError

        with pytest.raises(ParsingError):
            parse_resume(b"not a pdf at all", PDF_MIME)


class TestDocxParsing:
    def test_docx_roundtrip(self):
        content = make_docx(["Jane Doe", "Senior Python Engineer"])
        text = parse_resume(content, DOCX_MIME)
        assert "Jane Doe" in text
        assert "Senior Python Engineer" in text

    def test_corrupt_docx_raises_parsing_error(self):
        from app.services.parsing import ParsingError

        with pytest.raises(ParsingError):
            parse_resume(b"garbage bytes", DOCX_MIME)


class TestRouting:
    def test_unsupported_mime_rejected(self):
        with pytest.raises(UnsupportedFileTypeError):
            parse_resume(b"data", "image/png")

    def test_unsupported_error_names_the_type(self):
        with pytest.raises(UnsupportedFileTypeError, match="image/png"):
            parse_resume(b"data", "image/png")
