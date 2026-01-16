from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.prompts import ChatPromptTemplate

from app.core.llm import openai_llm


def build_streaming_chain():
    """Build and return a streaming chain configured with system prompt.

    The returned chain is suitable for streaming token-by-token responses.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a precise, reliable assistant designed to answer questions using retrieved documents and prior conversation context."
                "Rules you must follow:"
                "- Use the provided CONTEXT as your primary source of truth."
                "- Use the CONVERSATION HISTORY to maintain continuity, avoid repetition, and resolve references."
                "- If the answer is not explicitly supported by the context, say you don’t know."
                "- Do not invent facts, sources, or details."
                "- Do not reference internal tools, embeddings, vector databases, or retrieval mechanics."
                "- Do not mention that you are using documents unless explicitly asked."
                "- Be concise, clear, and structured in your responses."
                "- Prefer factual accuracy over verbosity."
                "- If a question is ambiguous, ask a brief clarifying question before answering."
                "- When relevant, explain reasoning step by step, but do not expose internal chain-of-thought."
                "- Maintain a professional, neutral, and helpful tone at all times."
                "Answer the user’s question based only on the information available to you.",
            ),
            ("system", "Context:\n{context}"),
            ("system", "Conversation history:\n{history}"),
            ("human", "{input}"),
        ]
    )
    openai_llm_instance = openai_llm()

    return create_stuff_documents_chain(openai_llm_instance, prompt)
