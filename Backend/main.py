# ============================================================
# MergePDF - FastAPI Backend
# ============================================================

import json
import os
import shutil
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from pypdf import PdfWriter


# ============================================================
# LOAD CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CONFIG_FILE = BASE_DIR / "config.json"

with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    config = json.load(file)


# ============================================================
# APPLICATION SETTINGS
# ============================================================

# Safely get the application dictionary, defaulting to an empty dict if missing
app_config = config.get("application", {})

# Safely get the version, defaulting to "0.0.1" if missing
APP_VERSION = app_config.get("version", "0.0.1")


HOST = config["server"]["host"]
PORT = config["server"]["port"]


# ============================================================
# PDF SETTINGS
# ============================================================

ALLOWED_EXTENSIONS = tuple(
    config["pdf"]["allowed_extensions"]
)

MAX_FILES = config["pdf"]["max_files"]

MAX_FILE_SIZE_MB = config["pdf"]["max_file_size_mb"]

MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

OUTPUT_FILENAME = config["pdf"]["output_filename"]


# ============================================================
# FOLDER SETTINGS
# ============================================================

UPLOAD_FOLDER = BASE_DIR / config["folders"]["upload"]

OUTPUT_FOLDER = BASE_DIR / config["folders"]["output"]

TEMPLATES_FOLDER = BASE_DIR / config["folders"]["templates"]

STATIC_FOLDER = BASE_DIR / config["folders"]["static"]


# ============================================================
# CREATE REQUIRED FOLDERS
# ============================================================

UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Merge multiple PDF files into one PDF file."
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_FOLDER)),
    name="static"
)


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory=str(TEMPLATES_FOLDER)
)


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "success",
        "application": APP_NAME,
        "message": "MergePDF backend is running"
    }


# ============================================================
# MERGE PDF FILES
# ============================================================

@app.post("/merge")
async def merge_pdfs(
    files: list[UploadFile] = File(...)
):

    # --------------------------------------------------------
    # CHECK NUMBER OF FILES
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


    # --------------------------------------------------------
    # CREATE PDF WRITER
    # --------------------------------------------------------

    writer = PdfWriter()

    uploaded_paths = []

    try:

        # ----------------------------------------------------
        # PROCESS EACH FILE
        # ----------------------------------------------------

        for index, uploaded_file in enumerate(files):

            filename = uploaded_file.filename or ""

            extension = Path(filename).suffix.lower()


            # ------------------------------------------------
            # CHECK FILE EXTENSION
            # ------------------------------------------------

            if extension not in ALLOWED_EXTENSIONS:

                raise HTTPException(
                    status_code=400,
                    detail=f"{filename} is not a valid PDF file."
                )


            # ------------------------------------------------
            # CREATE SAFE FILE NAME
            # ------------------------------------------------

            safe_filename = (
                f"file_{index + 1}{extension}"
            )

            file_path = UPLOAD_FOLDER / safe_filename


            # ------------------------------------------------
            # SAVE UPLOADED FILE
            # ------------------------------------------------

            file_size = 0

            with open(file_path, "wb") as buffer:

                while True:

                    chunk = await uploaded_file.read(1024 * 1024)

                    if not chunk:
                        break

                    file_size += len(chunk)


                    # ----------------------------------------
                    # CHECK FILE SIZE
                    # ----------------------------------------

                    if file_size > MAX_FILE_SIZE:

                        raise HTTPException(
                            status_code=400,
                            detail=(
                                f"{filename} exceeds the "
                                f"{MAX_FILE_SIZE_MB} MB limit."
                            )
                        )

                    buffer.write(chunk)


            uploaded_paths.append(file_path)


            # ------------------------------------------------
            # ADD PDF TO WRITER
            # ------------------------------------------------

            try:

                writer.append(str(file_path))

            except Exception:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"{filename} is corrupted or "
                        "is not a valid PDF."
                    )
                )


        # ----------------------------------------------------
        # OUTPUT FILE
        # ----------------------------------------------------

        output_path = OUTPUT_FOLDER / OUTPUT_FILENAME


        # Remove previous output file
        if output_path.exists():

            output_path.unlink()


        # ----------------------------------------------------
        # WRITE MERGED PDF
        # ----------------------------------------------------

        with open(output_path, "wb") as output_file:

            writer.write(output_file)


        # Close writer
        writer.close()


        # ----------------------------------------------------
        # RETURN MERGED PDF
        # ----------------------------------------------------

        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename=OUTPUT_FILENAME
        )


    except HTTPException:

        raise


    except Exception as error:

        print("Merge Error:", error)

        raise HTTPException(
            status_code=500,
            detail="An error occurred while merging PDF files."
        )


    finally:

        # ----------------------------------------------------
        # CLOSE UPLOADED FILES
        # ----------------------------------------------------

        for uploaded_file in files:

            await uploaded_file.close()


        # ----------------------------------------------------
        # DELETE TEMPORARY UPLOADS
        # ----------------------------------------------------

        for file_path in uploaded_paths:

            try:

                if file_path.exists():

                    file_path.unlink()

            except Exception as error:

                print(
                    f"Could not delete {file_path}: {error}"
                )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True
    )
