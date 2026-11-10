
import streamlit as st
import requests

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="Chat with Your Docs",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_URL = "http://127.0.0.1:8000"


# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown("""
<style>

/* Overall page */
.stApp {
    background: #F8FAFC;
    color: #1E293B;
}

.block-container {
    max-width: 1550px;
    padding: 1.5rem 1.5rem 1rem 1.5rem;
}

/* Hide default Streamlit elements */
#MainMenu, footer, header {
    visibility: hidden;
}

/* Panel cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 12px;
}

/* Headings */
h1, h2, h3 {
    color: #172554 !important;
}

h2 {
    font-size: 23px !important;
    font-weight: 700 !important;
}

h3 {
    font-size: 17px !important;
    font-weight: 650 !important;
}

/* Small text */
.stCaption {
    color: #64748B;
}

/* Buttons */
.stButton > button {
    background: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    min-height: 42px;
    font-weight: 600;
    font-size: 14px;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #1D4ED8;
    color: white;
    border: none;
}

/* Disabled button */
.stButton > button:disabled {
    background: #DBEAFE;
    color: #64748B;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #F8FAFC;
    border: 1px dashed #CBD5E1;
    border-radius: 10px;
    padding: 8px;
}

/* Text input */
.stTextInput input {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    color: #1E293B;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 12px 15px;
    margin-bottom: 12px;
}

/* Chat input */
[data-testid="stChatInput"] {
    border-radius: 12px;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 9px;
}

/* Dividers */
hr {
    border-color: #E2E8F0;
    margin: 12px 0;
}

/* Remove excess vertical spacing */
div[data-testid="stVerticalBlock"] {
    gap: 0.8rem;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------------
# SESSION STATE
# -----------------------------------

if "document_id" not in st.session_state:
    st.session_state.document_id = None

if "filename" not in st.session_state:
    st.session_state.filename = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------------
# MAIN TWO-PANEL LAYOUT
# -----------------------------------

left_panel, right_panel = st.columns(
    [0.30, 0.70],
    gap="medium"
)


# ===================================
# LEFT PANEL - DOCUMENTS
# ===================================

with left_panel:

    with st.container(border=True):

        st.markdown("## 📁 Documents")
        st.caption("Upload and manage your documents")

        st.divider()

        st.markdown("### Upload Documents")

        uploaded_file = st.file_uploader(
            "Choose a PDF",
            type=["pdf"],
            label_visibility="collapsed"
        )

        upload_clicked = st.button(
            "＋ Upload Document",
            use_container_width=True,
            disabled=uploaded_file is None
        )

        if upload_clicked:

            with st.spinner("Processing your PDF..."):

                try:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    }

                    response = requests.post(
                        f"{API_URL}/upload",
                        files=files,
                        timeout=180
                    )

                    response.raise_for_status()
                    result = response.json()

                    st.session_state.document_id = result["document_id"]
                    st.session_state.filename = result["filename"]
                    st.session_state.messages = []

                    st.success("Document processed successfully!")

                    st.rerun()

                except requests.exceptions.RequestException as error:
                    st.error(f"Upload failed: {error}")

        st.divider()

        st.markdown("### Your Documents")

        if st.session_state.document_id:

            st.markdown(
                f"""
                <div style="
                    background:#EFF6FF;
                    border:1px solid #DBEAFE;
                    border-radius:9px;
                    padding:12px;
                    margin:5px 0;
                ">
                    <span style="font-size:20px;">📄</span>
                    <span style="
                        color:#1E40AF;
                        font-weight:600;
                        margin-left:8px;
                    ">
                        {st.session_state.filename}
                    </span>
                    <div style="
                        color:#64748B;
                        font-size:12px;
                        margin-top:5px;
                    ">
                        Ready for questions
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.caption("No documents uploaded yet.")

        st.divider()

        st.caption("Supported format: PDF")
        st.caption("Powered by FastAPI · ChromaDB · Gemini")


# ===================================
# RIGHT PANEL - CHAT
# ===================================

with right_panel:

    with st.container(border=True):

        # Header
        header_col, action_col = st.columns([0.75, 0.25])

        with header_col:

            st.markdown("## AI Document Assistant")

            if st.session_state.filename:
                st.caption(
                    f"Currently using: {st.session_state.filename}"
                )
            else:
                st.caption("Your personal document question-answering assistant")

        with action_col:

            if st.button("↻ New Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

        st.divider()

        # Welcome message
        if not st.session_state.messages:

            with st.chat_message("assistant", avatar="🤖"):

                st.markdown(
                    """
                    **Hello! Welcome to Chat with Your Docs.**

                    Upload a PDF document and ask me anything about its
                    contents. I'll find relevant information and generate
                    answers with source references.
                    """
                )

        # Conversation history
        for message in st.session_state.messages:

            with st.chat_message(message["role"]):

                st.markdown(message["content"])

                if message.get("sources"):

                    with st.expander("📚 View source references"):

                        for index, source in enumerate(
                            message["sources"],
                            start=1
                        ):

                            metadata = source.get("metadata", {})
                            page = metadata.get(
                                "page_number",
                                "Unknown"
                            )

                            st.markdown(
                                f"**Source {index} · Page {page}**"
                            )

                            st.write(source.get("text", ""))

        # Chat input
        if st.session_state.document_id:

            prompt = st.chat_input(
                "Ask anything about your document..."
            )

        else:

            st.info(
                "📄 Upload a document from the left panel to start chatting."
            )

            prompt = None

        # Process question
        if prompt:

            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })

            try:

                with st.spinner("Finding the answer..."):

                    payload = {
                        "document_id": st.session_state.document_id,
                        "question": prompt
                    }

                    response = requests.post(
                        f"{API_URL}/ask",
                        json=payload,
                        timeout=180
                    )

                    response.raise_for_status()
                    result = response.json()

                    answer = result.get(
                        "answer",
                        "No answer returned."
                    )

                    sources = result.get("sources", [])

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

            except requests.exceptions.RequestException as error:

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Sorry, something went wrong: {error}"
                })

            st.rerun()
