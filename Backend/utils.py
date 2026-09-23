# ============================================================
# MergePDF - Utility Functions
# ============================================================

from pathlib import Path

from pypdf import PdfWriter, PdfReader


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {
    ".pdf"
}


# ============================================================
# CHECK PDF FILE
# ============================================================

def is_valid_pdf(filename: str) -> bool:
    """
    Check whether the uploaded file has a PDF extension.
    """

    if not filename:
        return False

    extension = Path(filename).suffix.lower()

    return extension in ALLOWED_EXTENSIONS


# ============================================================
# CHECK FILE SIZE
# ============================================================

def is_valid_file_size(
    file_size: int,
    max_size_mb: int
) -> bool:
    """
    Check whether the file size is within the allowed limit.
    """

    max_size_bytes = max_size_mb * 1024 * 1024

    return file_size <= max_size_bytes


# ============================================================
# VALIDATE PDF CONTENT
# ============================================================

def validate_pdf(file_path: str) -> bool:
    """
    Check whether a PDF file can be opened successfully.
    """

    try:

        reader = PdfReader(file_path)

        # Access pages to make sure the PDF is readable
        _ = len(reader.pages)

        return True

    except Exception:

        return False


# ============================================================
# MERGE PDF FILES
# ============================================================

def merge_pdf_files(
    input_files: list[str],
    output_file: str
) -> str:
    """
    Merge multiple PDF files into one PDF.

    Parameters:
        input_files: List of PDF file paths.
        output_file: Path of the merged PDF.

    Returns:
        Path of the merged PDF.
    """

    if not input_files:
        raise ValueError("No PDF files were provided.")

    if len(input_files) < 2:
        raise ValueError(
            "At least 2 PDF files are required."
        )


    writer = PdfWriter()


    try:

        # ----------------------------------------------------
        # ADD EACH PDF TO WRITER
        # ----------------------------------------------------

        for file_path in input_files:

            file_path = Path(file_path)

            if not file_path.exists():

                raise FileNotFoundError(
                    f"File not found: {file_path}"
                )


            if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:

                raise ValueError(
                    f"Invalid file type: {file_path.name}"
                )


            # Validate PDF before merging
            if not validate_pdf(str(file_path)):

                raise ValueError(
                    f"Invalid or corrupted PDF: "
                    f"{file_path.name}"
                )


            writer.append(str(file_path))


        # ----------------------------------------------------
        # CREATE OUTPUT DIRECTORY
        # ----------------------------------------------------

        output_path = Path(output_file)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        # ----------------------------------------------------
        # WRITE MERGED PDF
        # ----------------------------------------------------

        with open(output_path, "wb") as file:

            writer.write(file)


        return str(output_path)


    finally:

        writer.close()


# ============================================================
# DELETE FILE
# ============================================================

def delete_file(file_path: str) -> bool:
    """
    Delete a file safely.
    """

    try:

        path = Path(file_path)

        if path.exists():

            path.unlink()

            return True

        return False

    except Exception as error:

        print(
            f"Error deleting file {file_path}: {error}"
        )

        return False


# ============================================================
# DELETE MULTIPLE FILES
# ============================================================

def delete_files(file_paths: list[str]) -> None:
    """
    Delete multiple files.
    """

    for file_path in file_paths:

        delete_file(file_path)
