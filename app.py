from pathlib import Path

import streamlit as st

from ingestion.loadder import pdf_load
from chunking.chunker import split_docs
from embeddings.embed import get_embedding
from vector_store.faiss_store import create_embeddings
from retrieval.retriever import get_retriever
from prompt.prompt_temp import get_prompt
from llm.model import get_llm

DATA_DIR = Path(__file__).parent / "data"


@st.cache_resource(show_spinner="Reading and indexing the PDF (first time only)...")
def build_retriever(pdf_path):
    chunks = split_docs(pdf_load(pdf_path))
    vector_store = create_embeddings(chunks, get_embedding())
    return get_retriever(vector_store)


@st.cache_resource
def load_llm():
    return get_llm()


st.set_page_config(page_title="Textbook Tutor Bot", page_icon="📘")
st.title("📘 Textbook Tutor Bot")

pdfs = sorted(DATA_DIR.glob("*.pdf"))
if not pdfs:
    st.error("No PDF found. Put one in the data/ folder and reload.")
    st.stop()

with st.sidebar:
    pdf = st.selectbox("Book", pdfs, format_func=lambda p: p.name)
    if st.button("Clear chat"):
        st.session_state.messages = []

retriever = build_retriever(str(pdf))
prompt = get_prompt()
llm = load_llm()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask a question about the book"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        docs = retriever.invoke(question)
        context = "\n\n".join(doc.page_content for doc in docs)
        final_prompt = prompt.invoke({"context": context, "question": question})

        answer = st.write_stream(chunk.content for chunk in llm.stream(final_prompt))

        with st.expander("Sources"):
            for doc in docs:
                st.markdown(f"**Page {doc.metadata.get('page', 0) + 1}**")
                st.caption(doc.page_content[:500] + "...")

    st.session_state.messages.append({"role": "assistant", "content": answer})
