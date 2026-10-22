from langchain_ollama import ChatOllama


def get_llm():
    # Runs locally via Ollama; pull the model first: `ollama pull qwen3:1.7b`
    llm = ChatOllama(
        model="qwen3:1.7b",
        temperature=0.2,
        reasoning=False,
    )

    return llm
