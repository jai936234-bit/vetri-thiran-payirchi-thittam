import base64
import html
import os
from datetime import date

import requests
import streamlit as st

from dotenv import load_dotenv


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)


DOCUMENT_TYPES = [
    "Employment Contract",
    "Lease Agreement",
    "Non-Disclosure Agreement (NDA)",
    "Service Agreement",
    "Freelance Contract",
    "General Agreement"
]


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide"
)


# --------------------------------------------------
# CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    .title {
        text-align: center;
        font-size: 46px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: gray;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .preview {
        background: #171717;
        color: white;
        padding: 25px;
        border-radius: 12px;
        min-height: 500px;
        max-height: 700px;
        overflow-y: auto;
        white-space: pre-wrap;
        line-height: 1.6;
    }

    .warning {
        background: #fff3cd;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    '<div class="title">⚖️ LegalEase</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Legal Document Generator'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="warning">
    <b>Important:</b> LegalEase generates AI-assisted legal drafts.
    Always review important documents with a qualified legal professional
    before signing or using them.
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Session State
# --------------------------------------------------

if "document" not in st.session_state:

    st.session_state.document = ""


if "model" not in st.session_state:

    st.session_state.model = ""


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("Document Information")

    document_type = st.selectbox(
        "Document Type",
        DOCUMENT_TYPES
    )

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Jane Doe (Employee), "
            "TechNova Inc. (Employer)"
        ),
        height=100
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Salary is INR 800000 per year; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 30 days notice"
        ),
        height=180
    )

    effective_date = st.text_input(
        "Effective Date",
        value=date.today().strftime(
            "%B %d, %Y"
        )
    )

    jurisdiction = st.text_input(
        "Jurisdiction",
        value="India"
    )

    language = st.selectbox(
        "Language",
        [
            "English",
            "Tamil",
            "Hindi",
            "Spanish",
            "French"
        ]
    )

    logo = st.file_uploader(
        "Company Logo",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )

    generate_button = st.button(
        "🚀 Generate Document",
        type="primary",
        use_container_width=True
    )


# --------------------------------------------------
# Generate
# --------------------------------------------------

if generate_button:

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not terms.strip():

        st.error(
            "Please enter the terms and conditions."
        )

    elif not effective_date.strip():

        st.error(
            "Please enter an effective date."
        )

    else:

        payload = {

            "document_type":
                document_type,

            "parties":
                parties,

            "terms":
                terms,

            "effective_date":
                effective_date,

            "jurisdiction":
                jurisdiction,

            "language":
                language
        }

        with st.spinner(
            "Generating legal document..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=180
                )

                if response.status_code != 200:

                    try:
                        message = (
                            response
                            .json()
                            .get(
                                "detail",
                                "Unknown backend error"
                            )
                        )

                    except Exception:

                        message = response.text

                    st.error(message)

                else:

                    result = response.json()

                    st.session_state.document = (
                        result["content"]
                    )

                    st.session_state.model = (
                        result.get(
                            "model",
                            ""
                        )
                    )

                    st.success(
                        "Document generated successfully!"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to FastAPI. "
                    "Make sure the backend is running."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. "
                    "Please try again."
                )

            except Exception as error:

                st.error(
                    f"Error: {error}"
                )


# --------------------------------------------------
# Main Area
# --------------------------------------------------

left, right = st.columns(
    [1.5, 1]
)


# --------------------------------------------------
# Preview
# --------------------------------------------------

with left:

    st.subheader(
        "📄 Document Preview"
    )

    if st.session_state.document:

        safe_document = html.escape(
            st.session_state.document
        )

        st.markdown(
            f"""
            <div class="preview">
            {safe_document}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.info(
            "Generate a document to see the preview."
        )


# --------------------------------------------------
# Editing
# --------------------------------------------------

with right:

    st.subheader(
        "✏️ Edit Document"
    )

    edited_document = st.text_area(
        "Edit the generated document",
        value=st.session_state.document,
        height=500
    )

    if st.button(
        "💾 Save Changes",
        use_container_width=True
    ):

        st.session_state.document = (
            edited_document
        )

        st.success(
            "Changes saved."
        )


# --------------------------------------------------
# Downloads
# --------------------------------------------------

st.divider()

st.subheader(
    "⬇️ Download Document"
)


if st.session_state.document:

    # Logo → Base64

    logo_base64 = None

    if logo:

        encoded = base64.b64encode(
            logo.getvalue()
        ).decode("utf-8")

        logo_base64 = encoded


    export_payload = {

        "document_type":
            document_type,

        "content":
            st.session_state.document,

        "logo_base64":
            logo_base64
    }


    col1, col2, col3 = st.columns(3)


    # TXT

    with col1:

        if st.button(
            "Prepare TXT",
            use_container_width=True
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/export/txt",
                    json=export_payload,
                    timeout=60
                )

                response.raise_for_status()

                st.download_button(
                    "⬇ Download TXT",
                    response.content,
                    "legalease_document.txt",
                    "text/plain",
                    use_container_width=True
                )

            except Exception as error:

                st.error(
                    f"TXT export failed: {error}"
                )


    # DOCX

    with col2:

        if st.button(
            "Prepare DOCX",
            use_container_width=True
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/export/docx",
                    json=export_payload,
                    timeout=60
                )

                response.raise_for_status()

                st.download_button(
                    "⬇ Download DOCX",
                    response.content,
                    "legalease_document.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

            except Exception as error:

                st.error(
                    f"DOCX export failed: {error}"
                )


    # PDF

    with col3:

        if st.button(
            "Prepare PDF",
            use_container_width=True
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/export/pdf",
                    json=export_payload,
                    timeout=60
                )

                response.raise_for_status()

                st.download_button(
                    "⬇ Download PDF",
                    response.content,
                    "legalease_document.pdf",
                    "application/pdf",
                    use_container_width=True
                )

            except Exception as error:

                st.error(
                    f"PDF export failed: {error}"
                )


else:

    st.info(
        "Generate a document first to enable downloads."
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "LegalEase • AI-powered legal document drafting • "
    "Review generated documents professionally before use."
)

if st.session_state.model:

    st.caption(
        f"AI Model: {st.session_state.model}"
    )