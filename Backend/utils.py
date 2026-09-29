import io
from pypdf import PdfReader, PdfWriter


def validate_pdf_file(filename: str, content: bytes, max_size_mb: int = 50):
    """
    Validate an uploaded PDF file.
    """

    # Check filename
    if not filename:
        return False, "File name is missing."

    # Check extension
    if not filename.lower().endswith(".pdf"):
        return False, f"{filename} is not a PDF file."

    # Check empty file
    if not content:
        return False, f"{filename} is empty."

    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024

    if len(content) > max_size_bytes:
        return False, (
            f"{filename} exceeds the "
            f"{max_size_mb} MB file size limit."
        )

    # Check whether PDF can actually be read
    try:
        pdf_stream = io.BytesIO(content)
        reader = PdfReader(pdf_stream)

        # Access pages to make sure the PDF is readable
        len(reader.pages)

    except Exception:
        return False, f"{filename} is corrupted or cannot be read."

    return True, None


def merge_pdf_files(pdf_files):
    """
    Merge multiple PDF byte contents into one PDF.

    pdf_files should be a list of tuples:
    [
        ("file1.pdf", b"..."),
        ("file2.pdf", b"...")
    ]
    """

    writer = PdfWriter()

    for filename, content in pdf_files:

        pdf_stream = io.BytesIO(content)

        reader = PdfReader(pdf_stream)

        for page in reader.pages:
            writer.add_page(page)

    output = io.BytesIO()

    writer.write(output)

    output.seek(0)

    return output


def get_pdf_page_count(content: bytes):
    """
    Return the number of pages in a PDF.
    """

    pdf_stream = io.BytesIO(content)

    reader = PdfReader(pdf_stream)

    return len(reader.pages)


def get_file_size_mb(content: bytes):
    """
    Return file size in MB.
    """

    return len(content) / (1024 * 1024)
