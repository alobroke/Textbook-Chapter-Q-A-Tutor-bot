# Textbook-Chapter-QA-Tutor-bot

A Retrieval-Augmented Generation (RAG) chatbot that lets you ask questions about a PDF document and receive context-aware answers powered by a local LLM running in Ollama.

Instead of relying entirely on an LLM's internal knowledge, the chatbot retrieves relevant text chunks from the PDF using semantic similarity search with FAISS and passes them to the LLM as context.

Built with **Python, LangChain, Hugging Face, Sentence Transformers, FAISS, Ollama, and Streamlit**.

## Presentation

Project slides: [Textbook Tutor Bot PPT.pptx](Textbook%20Tutor%20Bot%20PPT.pptx)

## Features

- **PDF ingestion:** Extract text and page metadata using LangChain's `PyPDFLoader`.
- **Text chunking:** Split documents into overlapping chunks for efficient retrieval.
- **Semantic embeddings:** Convert text into vectors using `all-MiniLM-L6-v2`.
- **Vector search:** Retrieve the most relevant chunks using FAISS.
- **Local LLM answers:** Generate responses with `qwen3:1.7b` via Ollama. No API key needed.
- **Context-grounded prompting:** Instruct the LLM to answer using the retrieved document context.
- **Streamlit web UI:** Chat in the browser, with streamed answers and source pages.
- **Interactive CLI:** Ask multiple questions about the PDF in one session.
- **Modular architecture:** Separate components for ingestion, chunking, embeddings, retrieval, vector storage, prompting, and generation.

## Architecture

```text
                 PDF Document
                      |
                      v
                PDF Loader
                      |
                      v
               Extracted Text
                      |
                      v
                Text Splitter
                      |
                      v
                Text Chunks
                      |
                      v
             Embedding Model
          all-MiniLM-L6-v2
                      |
                      v
                FAISS Index
                      |
                      |
User Question --------+
      |
      v
   Retriever
      |
      v
Relevant PDF Chunks
      |
      v
 Prompt Template
      |
      v
 Ollama (qwen3:1.7b)
      |
      v
  Final Answer
```

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| LangChain | Document loading and RAG orchestration |
| PyPDF | PDF text extraction |
| Hugging Face | Embedding model integration |
| Sentence Transformers | Text embedding generation |
| `all-MiniLM-L6-v2` | Semantic embeddings |
| FAISS | Vector indexing and similarity search |
| Ollama (`qwen3:1.7b`) | Local answer generation |
| `langchain-ollama` | Ollama integration with LangChain |
| Streamlit | Web chat interface |

## Project Structure

```text
Textbook-Chapter-Q-A-Tutor-bot/
│
├── chunking/
│   └── chunker.py
│
├── data/
│   └── your_document.pdf
│
├── embeddings/
│   └── embed.py
│
├── ingestion/
│   └── loadder.py
│
├── llm/
│   └── model.py
│
├── prompt/
│   └── prompt_temp.py
│
├── retrieval/
│   └── retriever.py
│
├── vector_store/
│   └── faiss_store.py
│
├── .gitignore
├── app.py            # Streamlit web UI
├── main.py           # terminal chatbot
├── instruction.md    # beginner walkthrough
└── requirements.txt
```

> Note: The local directory and `loadder.py` filename retain their existing names. They can be renamed separately if desired.

## How It Works

### 1. PDF Ingestion

The PDF loader extracts the document's text and page metadata.

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader(pdf_path)
documents = loader.load()
```

Each page is represented as a LangChain `Document`.

### 2. Text Chunking

The extracted text is split using `RecursiveCharacterTextSplitter`.

Current configuration:

- Chunk size: 1,000 characters
- Chunk overlap: 200 characters

Overlapping chunks help preserve context across chunk boundaries.

### 3. Embedding Generation

The `all-MiniLM-L6-v2` embedding model converts each chunk into a numerical vector representing its semantic meaning.

### 4. FAISS Vector Store

FAISS indexes the document embeddings so that relevant chunks can be retrieved efficiently.

The current implementation creates the FAISS index in memory each time the application starts.

### 5. Retrieval

When a user submits a question, the retriever performs similarity search and returns the top three relevant chunks.

### 6. Prompt Construction

The retrieved chunks are combined into a context string and passed to the existing prompt template along with the user's question.

The prompt instructs the LLM to answer using the supplied context and to acknowledge when the answer is not present.

### 7. Answer Generation

The local Ollama model receives the constructed prompt and generates the final response, shown in the browser (Streamlit) or terminal (CLI).

## Installation and Setup

### Prerequisites

- Python 3.10+
- Git
- [Ollama](https://ollama.com) installed and running
- Internet for the first run (downloads packages and the embedding model)

### 1. Clone the Repository

```bash
git clone https://github.com/TusharParlikar/Textbook-Chapter-Q-A-Tutor-bot.git
cd Textbook-Chapter-Q-A-Tutor-bot
```

### 2. Pull the LLM

```bash
ollama pull qwen3:1.7b
```

To use a different model, pull it and change `model=` in `llm/model.py`.

### 3. Create a Virtual Environment and Install Dependencies

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt pypdf
```

**Linux / macOS**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pypdf
```

The first install is large (PyTorch is several hundred MB).

### 4. Add a PDF

Put a text-based PDF in the `data/` folder. Scanned PDFs (only images) need OCR first.

## Run the Chatbot

Activate the virtual environment first (step 3), then choose one:

### Option A: Web UI (recommended)

```bash
streamlit run app.py
```

Open http://localhost:8501. Pick a book in the sidebar, then ask questions. The first load takes about a minute to index the book. Each answer has a **Sources** dropdown with the pages it used.

### Option B: Terminal

Set the PDF filename in `main.py` (`pdf_path`), then:

```bash
python main.py
```

Type questions at the `Question:` prompt and `exit` to quit.

## Example Questions

- What is the difference between AI engineering and ML engineering?
- What is in-context learning?
- When should you finetune instead of using RAG?
- What is quantization?

For a step-by-step explanation of how the code works, see [instruction.md](instruction.md).

## Current Limitations

- Rebuilds the FAISS index every time the app starts.
- Retrieves a fixed number of chunks (`k=3`).
- Scanned PDFs need a separate OCR step.
- Answer quality depends on PDF extraction, retrieval relevance, and the local model's size.

## Future Improvements

- Persist the FAISS index to avoid re-embedding on every run.
- Support multiple PDFs in one knowledge base.
- Support scanned documents with OCR.
- Add retrieval evaluation.
