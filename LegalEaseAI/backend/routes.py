import base64
import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from PIL import Image

from backend.schemas import (
    DocumentRequest,
    GenerateResponse,
    ExportRequest
)

from backend.gemini_generator import (
    GeminiDocumentGenerator
)

from utils.exporters import (
    create_txt,
    create_docx,
    create_pdf
)


router = APIRouter()

generator = None


def get_generator():

    global generator

    if generator is None:
        generator = GeminiDocumentGenerator()

    return generator


@router.post(
    "/generate",
    response_model=GenerateResponse
)
def generate_document(
    request: DocumentRequest
):

    try:

        ai_generator = get_generator()

        document = ai_generator.generate_document(
            request
        )

        return GenerateResponse(
            document_type=request.document_type,
            content=document,
            model=ai_generator.model
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


def decode_logo(logo_base64):

    if not logo_base64:
        return None

    try:

        if "," in logo_base64:
            logo_base64 = logo_base64.split(",", 1)[1]

        image_data = base64.b64decode(
            logo_base64
        )

        image = Image.open(
            io.BytesIO(image_data)
        )

        if image.format not in [
            "PNG",
            "JPEG",
            "JPG"
        ]:
            raise ValueError(
                "Only PNG and JPG logos are supported."
            )

        return image_data

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid logo: {error}"
        )


@router.post("/export/txt")
def export_txt(request: ExportRequest):

    file_data = create_txt(
        request.content
    )

    return Response(
        content=file_data,
        media_type="text/plain",
        headers={
            "Content-Disposition":
            "attachment; filename=legalease_document.txt"
        }
    )


@router.post("/export/docx")
def export_docx(request: ExportRequest):

    logo = decode_logo(
        request.logo_base64
    )

    file_data = create_docx(
        request.content,
        request.document_type,
        logo
    )

    return Response(
        content=file_data,
        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        headers={
            "Content-Disposition":
            "attachment; filename=legalease_document.docx"
        }
    )


@router.post("/export/pdf")
def export_pdf(request: ExportRequest):

    logo = decode_logo(
        request.logo_base64
    )

    file_data = create_pdf(
        request.content,
        request.document_type,
        logo
    )

    return Response(
        content=file_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=legalease_document.pdf"
        }
    )