from pydantic import BaseModel, Field


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2)
    parties: str = Field(..., min_length=3)
    terms: str = Field(..., min_length=3)
    effective_date: str = Field(..., min_length=2)
    jurisdiction: str = "India"
    language: str = "English"


class GenerateResponse(BaseModel):
    document_type: str
    content: str
    model: str


class ExportRequest(BaseModel):
    document_type: str
    content: str
    logo_base64: str | None = None