# NoteIQ – RAG-Powered PDF Question Answering App
<img width="1919" height="918" alt="image" src="https://github.com/user-attachments/assets/5cc4eeb7-1f16-4127-9021-58e36b0821fc" />

**NoteIQ** is a student-friendly Retrieval-Augmented Generation (RAG) application that allows you to **upload PDFs, ingest them into a vector database, and query the content using an AI assistant**. Perfect for students, researchers, and professionals who need to quickly extract information from large documents.

The application uses OpenAI embeddings for semantic search, Qdrant as the vector store for efficient similarity search, and Inngest for reliable workflow orchestration.

---

## ✨ Features

- **📄 PDF Ingestion:** Upload PDFs which are automatically chunked, embedded, and stored in a vector database
- **🤖 RAG Query:** Ask questions about your uploaded PDFs and get context-aware, accurate answers
- **⚡ Rate-Limited Events:** Prevents excessive API calls, keeping usage cost-effective
- **🚀 FastAPI Backend:** High-performance backend handling ingestion, embedding, and querying workflows
- **🎨 Streamlit Frontend:** Clean and interactive UI for seamless document uploads and queries
- **🔍 Semantic Search:** Find relevant content even when using different terminology
- **📊 Document Management:** Track and manage multiple uploaded documents

---

## 🛠️ Tech Stack

- **Python 3.13** – Modern Python features and performance
- **Streamlit** – Interactive frontend UI framework
- **FastAPI** – High-performance async API server
- **Inngest** – Event-driven workflow orchestration and reliability
- **Qdrant** – High-performance vector database for embeddings
- **OpenAI API** – State-of-the-art embeddings & LLM inference
- **PyPDF2/pdfplumber** – PDF text extraction and processing
- **Pydantic** – Data validation and settings management

---

## 📦 Installation

### Prerequisites
- Python 3.13 or higher
- OpenAI API key
- Qdrant instance (local or cloud)
- Inngest account (for workflow orchestration)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/noteiq.git
   cd noteiq
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   # or
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or if using uv
   uv install
   ```

4. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   INNGEST_APP_ID=your_inngest_app_id
   INNGEST_SIGNING_KEY=your_inngest_signing_key_if_needed
   QDRANT_URL=your_qdrant_instance_url
   QDRANT_API_KEY=your_qdrant_api_key_if_any
   ```

5. **Start the Backend Server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Start the Frontend (in a new terminal)**
   ```bash
   streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
   ```

---

## 🚀 Usage

### Getting Started

1. **Access the Application**
   - Open your browser and navigate to `http://localhost:8501`
   - The Streamlit interface will load with upload and query options

2. **Upload a PDF Document**
   - Click on the file uploader in the Streamlit interface
   - Select your PDF file (supports multi-page documents)
   - The backend automatically triggers an Inngest workflow to:
     - Extract text from the PDF
     - Chunk the content into manageable pieces
     - Generate embeddings using OpenAI
     - Store embeddings in Qdrant vector database

3. **Query Your Documents**
   - Once ingestion is complete, use the chat interface
   - Ask questions about the PDF content in natural language
   - The AI assistant retrieves relevant context and provides accurate answers
   - Each query is rate-limited to control API usage and costs

### Example Queries
- "What are the main conclusions of this research paper?"
- "Summarize the methodology section"
- "What data sources were used in this study?"
- "Explain the key findings in simple terms"

---
---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key for embeddings and LLM | Yes |
| `INNGEST_APP_ID` | Inngest application identifier | Yes |
| `INNGEST_SIGNING_KEY` | Inngest webhook signing key | Optional |
| `QDRANT_URL` | Qdrant instance URL | Yes |
| `QDRANT_API_KEY` | Qdrant API key (if using cloud) | Optional |

### Qdrant Setup

**Option 1: Local Qdrant**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Option 2: Qdrant Cloud**
- Sign up at [Qdrant Cloud](https://cloud.qdrant.io/)
- Create a cluster and get your URL and API key






---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for powerful embeddings and LLM capabilities
- [Qdrant](https://qdrant.tech/) for efficient vector search
- [Inngest](https://inngest.com/) for reliable workflow orchestration
- [Streamlit](https://streamlit.io/) for rapid frontend development
- [FastAPI](https://fastapi.tiangolo.com/) for high-performance API framework

---

**Made with ❤️ for students and researchers who love learning from documents!**

