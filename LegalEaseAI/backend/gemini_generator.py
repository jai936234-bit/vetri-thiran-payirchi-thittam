import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.schemas import DocumentRequest

load_dotenv()


class GeminiDocumentGenerator:

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Please add it to your .env file."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

    def generate_document(
        self,
        request: DocumentRequest
    ) -> str:

        prompt = f"""
You are LegalEase, an AI legal-document drafting assistant.

Create a professional legal document draft using the information below.

DOCUMENT TYPE:
{request.document_type}

PARTIES:
{request.parties}

TERMS AND CONDITIONS:
{request.terms}

EFFECTIVE DATE:
{request.effective_date}

JURISDICTION:
{request.jurisdiction}

LANGUAGE:
{request.language}

IMPORTANT RULES:

1. Create a complete structured legal document.
2. Do not invent important facts.
3. Do not invent names, dates, amounts or addresses.
4. If information is missing, use [INSERT DETAILS].
5. Use professional legal language.
6. Include a clear title.
7. Include parties.
8. Include effective date.
9. Include relevant numbered clauses.
10. Include the supplied terms.
11. Include signature sections where appropriate.
12. Do not put the answer inside Markdown code fences.
13. Return only the document.
14. This is a legal draft and should be reviewed by a qualified legal professional.

Generate the document now.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=12000
            )
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        return response.text.strip()