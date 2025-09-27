import asyncio
from pathlib import Path
import time
import os
import requests

import streamlit as st
import inngest
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="RAG Chat", page_icon="🤖", layout="wide")

# -------------------------------
# Inngest Client Setup
# -------------------------------
@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(app_id="rag_app", is_production=False)


def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_bytes = file.getbuffer()
    file_path.write_bytes(file_bytes)
    return file_path


async def send_rag_ingest_event(pdf_path: Path) -> None:
    client = get_inngest_client()
    await client.send(
        inngest.Event(
            name="rag/inngest_pdf",
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )


async def send_rag_query_event(question: str, top_k: int) -> str:
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/query_pdf_ai",
            data={
                "query": question,
                "top_k": top_k,
            },
        )
    )
    return result[0]


def _inngest_api_base() -> str:
    return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")


def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


def wait_for_run_output(event_id: str, timeout_s: float = 120.0, poll_interval_s: float = 0.5) -> dict:
    start = time.time()
    last_status = None
    while True:
        runs = fetch_runs(event_id)
        if runs:
            run = runs[0]
            status = run.get("status")
            last_status = status or last_status
            if status in ("Completed", "Succeeded", "Success", "Finished"):
                return run.get("output") or {}
            if status in ("Failed", "Cancelled"):
                raise RuntimeError(f"Function run {status}")
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out waiting for run output (last status: {last_status})")
        time.sleep(poll_interval_s)


# -------------------------------
# UI Layout (Split Screen)
# -------------------------------
col1, col2 = st.columns([1, 2])  # left for upload, right for chat

# -------------------------------
# Left Panel → Upload PDFs
# -------------------------------
with col1:
    st.header("📄 PDF Uploads")
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"], accept_multiple_files=False)

    if uploaded is not None:
        with st.spinner("Uploading and triggering ingestion..."):
            path = save_uploaded_pdf(uploaded)
            asyncio.run(send_rag_ingest_event(path))
            time.sleep(0.3)
        st.success(f"Ingested: {path.name}")
        st.caption("Upload another PDF if needed.")

# -------------------------------
# Right Panel → Chat with RAG
# -------------------------------
with col2:
    st.header("💬 Chat with your PDFs")

    # initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # display past messages
    for msg in st.session_state.messages:
        role, content = msg["role"], msg["content"]
        if role == "user":
            st.chat_message("user").markdown(content)
        else:
            st.chat_message("assistant").markdown(content)

    # chat input
    if question := st.chat_input("Ask something about your PDFs..."):
        # save user message
        st.session_state.messages.append({"role": "user", "content": question})
        st.chat_message("user").markdown(question)

        with st.spinner("Thinking..."):
            event_id = asyncio.run(send_rag_query_event(question.strip(), 5))
            output = wait_for_run_output(event_id)
            answer = output.get("answer", "(No answer)")
            sources = output.get("sources", [])

        # save assistant reply
        response_text = answer
        if sources:
            response_text += "\n\n**Sources:**\n" + "\n".join(f"- {s}" for s in sources)

        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.chat_message("assistant").markdown(response_text)
