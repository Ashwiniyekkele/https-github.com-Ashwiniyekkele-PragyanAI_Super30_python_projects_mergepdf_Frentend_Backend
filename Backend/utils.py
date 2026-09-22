# ============================================================

# backend/utils.py

# PragyanAI PDF Merger

# ============================================================

import io

from pypdf import PdfReader, PdfWriter

# ============================================================

# SUPPORTED FILE TYPE

# ============================================================

ALLOWED_PDF_TYPE = "application/pdf"

# ============================================================

# VALIDATE PDF TYPE

# ============================================================

def validate_pdf_type(content_type: str) -> bool:
"""
Validate uploaded PDF MIME type.

```
Parameters
----------
content_type : str
    MIME type received from uploaded file.

Returns
-------
bool
    True if file type is PDF.
"""

return content_type == ALLOWED_PDF_TYPE
```

# ============================================================

# VALIDATE PDF FILE

# ============================================================

def validate_pdf_file(file_bytes: bytes) -> bool:
"""
Check whether uploaded bytes contain a valid PDF.

```
Parameters
----------
file_bytes : bytes
    Uploaded PDF file bytes.

Returns
-------
bool
    True if PDF is valid.
"""

if not file_bytes:

    raise ValueError(
        "Uploaded PDF file is empty."
    )

try:

    pdf_stream = io.BytesIO(
        file_bytes
    )

    reader = PdfReader(
        pdf_stream
    )

    # ----------------------------------------------------
```
