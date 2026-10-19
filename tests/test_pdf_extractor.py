"""
Tests for pdf_extractor.py

We generate small PDFs on-the-fly using PyMuPDF itself (fitz), so these
tests don't depend on any external sample files.
"""

import fitz
import pytest

from src.pdf_extractor import extract_text_from_pdf, PDFExtractionError


def make_pdf_bytes(text: str) -> bytes:
    """Helper: create a simple one-page PDF containing `text`."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_extract_text_from_valid_pdf():
    pdf_bytes = make_pdf_bytes("Python Developer Resume")
    text = extract_text_from_pdf(pdf_bytes)
    assert "Python" in text
    assert "Developer" in text


def test_empty_bytes_raises_error():
    with pytest.raises(PDFExtractionError):
        extract_text_from_pdf(b"")


def test_invalid_pdf_bytes_raises_error():
    with pytest.raises(PDFExtractionError):
        extract_text_from_pdf(b"this is not a real pdf file")


def test_multi_page_pdf_extracts_all_pages():
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((72, 72), "First page content")
    page2 = doc.new_page()
    page2.insert_text((72, 72), "Second page content")
    pdf_bytes = doc.tobytes()
    doc.close()

    text = extract_text_from_pdf(pdf_bytes)
    assert "First page" in text
    assert "Second page" in text


def test_scanned_image_only_pdf_raises_error():
    """
    A scanned resume (image only, no text layer) should raise a clear,
    user-friendly error rather than silently returning empty text.
    We simulate this with a blank page that has no inserted text at all.
    """
    doc = fitz.open()
    doc.new_page()  # blank page, no text layer
    pdf_bytes = doc.tobytes()
    doc.close()

    with pytest.raises(PDFExtractionError):
        extract_text_from_pdf(pdf_bytes)


def test_oversized_pdf_is_rejected_without_parsing(monkeypatch):
    from src import pdf_extractor

    monkeypatch.setattr(pdf_extractor, "MAX_PDF_BYTES", 4)
    with pytest.raises(PDFExtractionError, match="too large"):
        pdf_extractor.extract_text_from_pdf(b"12345")


def test_pdf_with_too_many_pages_is_rejected():
    from src import pdf_extractor

    doc = fitz.open()
    for _ in range(pdf_extractor.MAX_PDF_PAGES + 1):
        doc.new_page()
    data = doc.tobytes()
    doc.close()
    with pytest.raises(PDFExtractionError, match="no more than"):
        extract_text_from_pdf(data)
