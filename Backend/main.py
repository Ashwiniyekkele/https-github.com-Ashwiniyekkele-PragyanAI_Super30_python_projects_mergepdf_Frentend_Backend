import json
import shutil
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from utils import merge_pdf_files


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CONFIG_FILE = BASE_DIR / "config.json"
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD CONFIGURATION
# ============================================================

with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    config = json.load(file)


APP_NAME = config["app_name"]
APP_VERSION = config["version"]

MAX_UPLOAD_SIZE_MB = config["max_upload_size_mb"]
MAX_FILES = config["max_files"]

ALLOWED_FILE_TYPES = tuple(
    extension.lower()
    for extension in config["allowed_file_types"]
)

OUTPUT_FILENAME = config["output_filename"]

CORS_ORIGINS = config["cors_origins"]


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def home():
    return {
        "message": "MergePDF API is running",
        "application": APP_NAME,
        "version": APP_VERSION
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


# ============================================================
# MERGE PDF
# ============================================================

@app.post("/merge")
async def merge_pdfs(
    files: list[UploadFile] = File(...)
):

    # --------------------------------------------------------
    # Check number of files
    # --------------------------------------------------------

    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least 2 PDF files."
        )

    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"You can upload maximum {MAX_FILES} PDF files."
        )


    uploaded_files = []

    try:

        # ----------------------------------------------------
        # Save uploaded files
        # ----------------------------------------------------

        for index, uploaded_file in enumerate(files):

            if not uploaded_file.filename:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file name."
                )

            extension = Path(
                uploaded_file.filename
            ).suffix.lower()

            if extension not in ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Only PDF files are allowed: "
                           f"{uploaded_file.filename}"
                )

            file_path = (
                UPLOAD_DIR /
                f"{index}_{Path(uploaded_file.filename).name}"
            )

            content = await uploaded_file.read()

            max_size_bytes = (
                MAX_UPLOAD_SIZE_MB * 1024 * 1024
            )

            if len(content) > max_size_bytes:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"{uploaded_file.filename} is larger than "
                        f"{MAX_UPLOAD_SIZE_MB} MB."
                    )
                )

            with open(file_path, "wb") as file:
                file.write(content)

            uploaded_files.append(str(file_path))


        # ----------------------------------------------------
        # Output file
        # ----------------------------------------------------

        output_file = OUTPUT_DIR / OUTPUT_FILENAME


        # ----------------------------------------------------
        # Merge PDFs
        # ----------------------------------------------------

        merge_pdf_files(
            uploaded_files,
            str(output_file)
        )


        # ----------------------------------------------------
        # Return merged PDF
        # ----------------------------------------------------

        return FileResponse(
            path=str(output_file),
            media_type="application/pdf",
            filename=OUTPUT_FILENAME
        )


    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"PDF merge failed: {str(error)}"
        )

    finally:

        # ----------------------------------------------------
        # Delete temporary uploaded files
        # ----------------------------------------------------

        for file_path in uploaded_files:

            try:

                path = Path(file_path)

                if path.exists():
                    path.unlink()

            except Exception:
                pass


# ============================================================
# DOWNLOAD ENDPOINT
# ============================================================

@app.get("/download")
async def download_pdf():

    output_file = OUTPUT_DIR / OUTPUT_FILENAME

    if not output_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Merged PDF not found."
        )

    return FileResponse(
        path=str(output_file),
        media_type="application/pdf",
        filename=OUTPUT_FILENAME
)
