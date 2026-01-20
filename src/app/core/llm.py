from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import settings


def openai_llm(
    model_name: str = settings.LLM_MODEL,
    temperature: float = 0.2,
    streaming: bool = True,
) -> ChatOpenAI:
    """Create and return a configured ChatOpenAI instance.

    Args:
        model_name (str): model identifier.
        temperature (float): sampling temperature.
        streaming (bool): whether to enable streaming responses.

    Returns:
        ChatOpenAI: configured LLM client.
    """
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        streaming=streaming,
        api_key=settings.LLM_API_KEY,
    )


def embedding_function(model_name: str = settings.EMBEDDING_MODEL) -> OpenAIEmbeddings:
    """Return an OpenAI embeddings client configured for the project.

    Args:
        model_name (str): embedding model to use.

    Returns:
        OpenAIEmbeddings: embeddings client.
    """
    return OpenAIEmbeddings(api_key=settings.LLM_API_KEY, model=model_name)
