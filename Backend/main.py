# ============================================================

# backend/main.py

# PragyanAI PDF Merger

# FastAPI Backend

# ============================================================

import json
from pathlib import Path
from io import BytesIO

from fastapi import (
FastAPI,
File,
HTTPException,
UploadFile
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from pypdf import PdfReader, PdfWriter

# ============================================================

# APPLICATION PATH

# ============================================================

BASE_DIR = Path(**file**).resolve().parent

CONFIG_FILE = BASE_DIR / "config.json"

# ============================================================

# DEFAULT CONFIGURATION

# ============================================================

DEFAULT_CONFIG = {

```
"app_name":
    "PragyanAI PDF Merger",

"version":
    "1.0.0",

"description":
    "PDF Merger using FastAPI and PyPDF",

"cors_origins": [
    "*"
],

"max_upload_size_mb":
    10
```

}

# ============================================================

# LOAD CONFIGURATION

# ============================================================

def load_config():

```
"""
Load application configuration from config.json.
"""

try:

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        loaded_config = json.load(file)

    # ----------------------------------------------------
    # Merge loaded configuration with defaults
    # ----------------------------------------------------

    config = {
        **DEFAULT_CONFIG,
        **loaded_config
    }

    return config

except FileNotFoundError:

    print(
        "WARNING: config.json not found. "
        "Using default configuration."
    )

    return DEFAULT_CONFIG

except json.JSONDecodeError:

    print(
        "WARNING: config.json contains invalid JSON. "
        "Using default configuration."
    )

    return DEFAULT_CONFIG
```

# ============================================================

# APPLICATION CONFIGURATION

# ============================================================

config = load_config()

APP_NAME = config.get(
"app_name",
DEFAULT_CONFIG["app_name"]
)

APP_VERSION = config.get(
"version",
DEFAULT_CONFIG["version"]
)

APP_DESCRIPTION = config.get(
"description",
DEFAULT_CONFIG["description"]
)

CORS_ORIGINS = config.get(
"cors_origins",
DEFAULT_CONFIG["cors_origins"]
)

MAX_UPLOAD_SIZE_MB = config.get(
"max_upload_size_mb",
DEFAULT_CONFIG["max_upload_size_mb"]
)

MAX_UPLOAD_SIZE = (
MAX_UPLOAD_SIZE_MB
* 1024
* 1024
)

# ============================================================

# FASTAPI APPLICATION

# ============================================================

app = FastAPI(

```
title=APP_NAME,

description=APP_DESCRIPTION,

version=APP_VERSION,

docs_url="/docs",

redoc_url="/redoc"
```

)

# ============================================================

# CORS CONFIGURATION

# ============================================================

app.add_middleware(

```
CORSMiddleware,

allow_origins=CORS_ORIGINS,

allow_credentials=False,

allow_methods=[
    "GET",
    "POST"
],

allow_headers=[
    "*"
]
```

)

# ============================================================

# ROOT ENDPOINT

# ============================================================

@app.get("/")
def root():

```
"""
Root API endpoint.

Returns basic information about the application,
available endpoints and documentation.
"""

return {

    "success": True,

    "message":
        "PragyanAI PDF Merger API is running",

    "application":
        APP_NAME,

    "version":
        APP_VERSION,

    "status":
        "online",

    "documentation": {

        "swagger":
            "/docs",

        "redoc":
            "/redoc"
    },

    "endpoints": {

        "merge":
            "POST /merge",

        "health":
            "GET /health",

        "info":
            "GET /info"
    },

    "technologies": [

        "Python",

        "FastAPI",

        "PyPDF"
    ]
}
```

# ============================================================

# HEALTH CHECK

# ============================================================

@app.get("/health")
def health():

```
"""
Health check endpoint.

Useful for:
- Cloud deployment
- Monitoring
- Testing
- Load balancers
"""

return {

    "success": True,

    "status":
        "healthy",

    "service":
        "PDF Merger API",

    "version":
        APP_VERSION,

    "components": {

        "fastapi":
            "running",

        "pypdf":
            "available"
    }
}
```

# ============================================================

# MERGE PDF FILES

# ============================================================

@app.post("/merge")
async def merge_pdfs(

```
files: list[UploadFile] = File(...)
```

):

```
"""
Merge multiple PDF files into one PDF.

Request:
    multipart/form-data

Field name:
    files

Response:
    Merged PDF file
"""

# --------------------------------------------------------
# Validate number of files
# --------------------------------------------------------

if len(files) < 2:

    raise HTTPException(

        status_code=400,

        detail=
            "Please upload at least 2 PDF files."
    )


# --------------------------------------------------------
# Create PDF writer
# --------------------------------------------------------

writer = PdfWriter()


try:

    # ----------------------------------------------------
    # Process each uploaded PDF
    # ----------------------------------------------------

    for file in files:

        # ------------------------------------------------
        # Validate filename
        # ------------------------------------------------

        if not file.filename:

            raise HTTPException(

                status_code=400,

                detail=
                    "One of the uploaded files has no filename."
            )


        # ------------------------------------------------
        # Validate PDF extension
        # ------------------------------------------------

        if not file.filename.lower().endswith(".pdf"):

            raise HTTPException(

                status_code=400,

                detail=(
                    f"{file.filename} is not a PDF file. "
                    "Please upload only PDF files."
                )
            )


        # ------------------------------------------------
        # Read file
        # ------------------------------------------------

        contents = await file.read()


        # ------------------------------------------------
        # Check empty file
        # ------------------------------------------------

        if not contents:

            raise HTTPException(

                status_code=400,

                detail=(
                    f"{file.filename} is empty."
                )
            )


        # ------------------------------------------------
        # Check file size
        # ------------------------------------------------

        if len(contents) > MAX_UPLOAD_SIZE:

            raise HTTPException(

                status_code=413,

                detail=(
                    f"{file.filename} exceeds the maximum "
                    f"allowed size of "
                    f"{MAX_UPLOAD_SIZE_MB} MB."
                )
            )


        # ------------------------------------------------
        # Read PDF
        # ------------------------------------------------

        pdf_stream = BytesIO(contents)

        reader = PdfReader(pdf_stream)


        # ------------------------------------------------
        # Check PDF pages
        # ------------------------------------------------

        if len(reader.pages) == 0:

            raise HTTPException(

                status_code=400,

                detail=(
                    f"{file.filename} does not contain "
```
