# Textbook Tutor Bot: How It Works and How to Run It

## What this project is

A chatbot that answers questions about **one PDF book**. You type a question in the terminal, and the bot:

1. finds the 3 passages of the book most related to your question, and
2. gives those passages to a local LLM (via Ollama) with the instruction "answer only from this text".

This technique is called **RAG (Retrieval-Augmented Generation)**. The LLM doesn't have to "know" the book; it reads the relevant pages each time you ask. If the answer isn't in those pages, it is told to say *"I don't know based on the provided context."*

## The big picture

```
                 ONE-TIME SETUP (every time you start main.py)
 PDF ──► load pages ──► split into chunks ──► turn chunks into vectors ──► FAISS index

                 FOR EVERY QUESTION
 question ──► vector ──► FAISS finds 3 closest chunks ──► prompt (chunks + question) ──► Ollama LLM ──► answer
```

## Each file, in the order it runs

| Step | File | What it does |
|------|------|--------------|
| 1 | [ingestion/loadder.py](ingestion/loadder.py) | `PyPDFLoader` reads the PDF and returns one `Document` per page (text + page number). |
| 2 | [chunking/chunker.py](chunking/chunker.py) | Splits pages into chunks of ~1000 characters with a 200-character overlap, so a sentence cut at a boundary still appears whole in one chunk. |
| 3 | [embeddings/embed.py](embeddings/embed.py) | Loads `all-MiniLM-L6-v2`, a small Hugging Face model that turns text into a list of 384 numbers (a *vector*). Texts with similar meaning get similar vectors. |
| 4 | [vector_store/faiss_store.py](vector_store/faiss_store.py) | Embeds every chunk and stores the vectors in a **FAISS** index, a fast "find the nearest vectors" database kept in memory. |
| 5 | [retrieval/retriever.py](retrieval/retriever.py) | Wraps FAISS as a retriever that returns the `k=3` most similar chunks for a question. |
| 6 | [prompt/prompt_temp.py](prompt/prompt_temp.py) | The prompt template: rules ("use ONLY the context…") + `{context}` + `{question}`. |
| 7 | [llm/model.py](llm/model.py) | Creates the LLM: `qwen3:1.7b` running locally through Ollama. |
| — | [main.py](main.py) | Wires steps 1–7 together, then loops: read question → retrieve → build prompt → ask LLM → print answer. Type `exit` to quit. |

## Setup (Windows, PowerShell)

### 1. Install Ollama and the model

Install Ollama from https://ollama.com, then:

```powershell
ollama pull qwen3:1.7b
```

Ollama must be running in the background (it starts automatically after install).

### 2. Create the virtual environment and install packages

From the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt pypdf
```

The first install is large (PyTorch is several hundred MB).

### 3. Put your PDF in `data/`

Then set the file name in [main.py](main.py) (the `pdf_path` near the top) to match it.

### 4. Run

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

Wait for `PDF RAG Chatbot is Ready!`, then ask questions.

## Things to know

- **Startup is slow for big books.** The whole PDF is re-embedded every time you start `main.py`; nothing is saved to disk. A 500-page book can take a few minutes on CPU. (The fix would be `vector_store.save_local(...)` once and `FAISS.load_local(...)` afterwards.)
- **The first run downloads the embedding model** (~90 MB) from Hugging Face. Later runs use the cached copy.
- **Answer quality depends on retrieval.** If the 3 retrieved chunks don't contain the answer, the bot says it doesn't know, even if the book covers it elsewhere. Raising `k` in [retrieval/retriever.py](retrieval/retriever.py) gives the LLM more context, but it gets slower.
- **`qwen3:1.7b` is small.** It's fast but sometimes vague. For better answers, pull a bigger model (e.g. `ollama pull qwen3:8b`) and change the name in [llm/model.py](llm/model.py).
- **Scanned PDFs (images only) won't work**: there is no text to extract without OCR.

## Common changes

| I want to… | Change |
|-----------|--------|
| Use a different book | Drop the PDF in `data/`, update `pdf_path` in [main.py](main.py) |
| Use a different LLM | `model=` in [llm/model.py](llm/model.py) (must be pulled in Ollama first) |
| Get longer/shorter chunks | `chunk_size` / `chunk_overlap` in [chunking/chunker.py](chunking/chunker.py) |
| Retrieve more passages | `k` in [retrieval/retriever.py](retrieval/retriever.py) |
| Change the bot's tone or rules | The template text in [prompt/prompt_temp.py](prompt/prompt_temp.py) |
