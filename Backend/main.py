from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from pypdf import PdfReader, PdfWriter

import io
import json
import os


# =========================================================
# LOAD CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

with open(CONFIG_FILE, "r") as file:
    config = json.load(file)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title=config.get("app_name", "PDF Merger API"),
    version=config.get("version", "1.0.0")
)


# =========================================================
# CORS CONFIGURATION
# =========================================================

allowed_origins = config.get(
    "allowed_origins",
    ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# HOME ROUTE
# =========================================================

@app.get("/")
def home():

    return {
        "message": "PDF Merger API is running successfully!",
        "app": config.get("app_name", "PDF Merger API"),
        "version": config.get("version", "1.0.0")
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "message": "Backend is working correctly"
    }


# =========================================================
# MERGE PDF FILES
# =========================================================

@app.post("/merge")
async def merge_pdfs(
    files: list[UploadFile] = File(...)
):

    # -----------------------------------------------------
    # CHECK NUMBER OF FILES
    # -----------------------------------------------------

    max_files = config.get("max_files", 20)

    if len(files) < 2:

        raise HTTPException(
            status_code=400,
            detail="Please upload at least 2 PDF files."
        )

    if len(files) > max_files:

        raise HTTPException(
            status_code=400,
            detail=f"You can upload a maximum of {max_files} PDF files."
        )


    # -----------------------------------------------------
    # CREATE PDF WRITER
    # -----------------------------------------------------

    writer = PdfWriter()

    valid_files = 0


    # -----------------------------------------------------
    # PROCESS EACH PDF
    # -----------------------------------------------------

    for file in files:

        # Check file name
        if not file.filename:

            continue


        # Check PDF extension
        if not file.filename.lower().endswith(".pdf"):

            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} is not a PDF file."
            )


        # Read file
        content = await file.read()


        # Check empty file
        if not content:

            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} is empty."
            )


        # -------------------------------------------------
        # CHECK FILE SIZE
        # -------------------------------------------------

        max_file_size_mb = config.get(
            "max_file_size_mb",
            50
        )

        max_file_size_bytes = (
            max_file_size_mb * 1024 * 1024
        )

        if len(content) > max_file_size_bytes:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"{file.filename} exceeds the "
                    f"{max_file_size_mb} MB limit."
                )
            )


        # -------------------------------------------------
        # READ PDF
        # -------------------------------------------------

        try:

            pdf_stream = io.BytesIO(content)

            reader = PdfReader(pdf_stream)


            # -------------------------------------------------
            # ADD ALL PAGES
            # -------------------------------------------------

            for page in reader.pages:

                writer.add_page(page)


            valid_files += 1


        except Exception as error:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Could not read {file.filename}: "
                    f"{str(error)}"
                )
            )


    # -----------------------------------------------------
    # CHECK VALID FILES
    # -----------------------------------------------------

    if valid_files < 2:

        raise HTTPException(
            status_code=400,
            detail="Please provide at least 2 valid PDF files."
        )


    # -----------------------------------------------------
    # CREATE MERGED PDF
    # -----------------------------------------------------

    output = io.BytesIO()

    try:

        writer.write(output)

        output.seek(0)

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create merged PDF: {str(error)}"
        )


    # -----------------------------------------------------
    # DOWNLOAD RESPONSE
    # -----------------------------------------------------

    output_filename = config.get(
        "output_filename",
        "merged.pdf"
    )

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{output_filename}"'
        }
    )


# =========================================================
# RUN LOCALLY
# =========================================================

if __name__ == "__main__":

    import uvicorn

    host = config.get(
        "host",
        "0.0.0.0"
    )

    port = int(
        config.get(
            "port",
            8000
        )
    )

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )
