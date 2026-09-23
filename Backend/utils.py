from pathlib import Path

from pypdf import PdfWriter, PdfReader


ALLOWED_EXTENSIONS = {".pdf"}


def is_valid_pdf(filename: str) -> bool:

    if not filename:
        return False

    extension = Path(filename).suffix.lower()

    return extension in ALLOWED_EXTENSIONS


def validate_pdf(file_path: str) -> bool:

    try:

        reader = PdfReader(file_path)

        len(reader.pages)

        return True

    except Exception:

        return False


def merge_pdf_files(
    input_files: list[str],
    output_file: str
) -> str:

    if not input_files:
        raise ValueError(
            "No PDF files were provided."
        )

    if len(input_files) < 2:
        raise ValueError(
            "At least 2 PDF files are required."
        )

    writer = PdfWriter()

    try:

        for file_path in input_files:

            path = Path(file_path)

            if not path.exists():
                raise FileNotFoundError(
                    f"File not found: {path}"
                )

            if path.suffix.lower() not in ALLOWED_EXTENSIONS:
                raise ValueError(
                    f"Invalid file type: {path.name}"
                )

            if not validate_pdf(str(path)):
                raise ValueError(
                    f"Invalid or corrupted PDF: {path.name}"
                )

            writer.append(str(path))


        output_path = Path(output_file)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(output_path, "wb") as file:

            writer.write(file)


        return str(output_path)

    finally:

        writer.close()
