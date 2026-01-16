from langchain_chroma import Chroma

from app.core.config import settings
from app.core.llm import embedding_function


def get_vectorstore():
    """Get a configured Chroma vector store instance.

    Returns:
        Chroma: a Chroma client configured with the project's settings and
        embedding function.
    """
    return Chroma(
        persist_directory=settings.CHROMA_PATH,
        embedding_function=embedding_function(),
        collection_name="documents",
    )
