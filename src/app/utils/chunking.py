from langchain_classic.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import settings


def chunk_text(text: str):
    """Split a single string into chunked pieces using configured sizes.

    Args:
        text (str): the input text to chunk.

    Returns:
        List[str]: list of text chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    return splitter.split_text(text)


def chunk_documents(documents):
    """Split a list of LangChain Document objects into chunked documents.

    Args:
        documents (List[Document]): documents to chunk.

    Returns:
        List[Document]: chunked document objects.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)
