from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pypdf import PdfReader, PdfWriter
import io

app = FastAPI()

# Allow Netlify frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "PDF Merger Backend is running"
    }


@app.post("/merge")
async def merge_pdfs(files: list[UploadFile] = File(...)):

    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please select at least 2 PDF files."
        )

    writer = PdfWriter()

    try:
        for file in files:

            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=400,
                    detail=f"{file.filename} is not a PDF file."
                )

            content = await file.read()

            pdf_file = io.BytesIO(content)

            reader = PdfReader(pdf_file)

            for page in reader.pages:
                writer.add_page(page)

        output = io.BytesIO()

        writer.write(output)
        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                "attachment; filename=merged.pdf"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF merging failed: {str(e)}"
        )
