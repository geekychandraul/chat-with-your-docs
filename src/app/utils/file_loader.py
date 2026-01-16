import tempfile

from fastapi import UploadFile
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader


def load_documents(upload_file: UploadFile):
    """Load documents from an uploaded file into LangChain document objects.

    Supports PDF, TXT/MD, and DOCX file types.

    Args:
        upload_file (UploadFile): a Starlette/FastAPI UploadFile instance.

    Returns:
        List[Document]: documents loaded by the appropriate loader.
    """
    suffix = upload_file.filename.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
        tmp.write(upload_file.file.read())
        tmp_path = tmp.name

    if suffix == "pdf":
        loader = PyPDFLoader(tmp_path)
    elif suffix in {"txt", "md"}:
        loader = TextLoader(tmp_path)
    elif suffix in {"docx"}:
        loader = Docx2txtLoader(tmp_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    # TODO capability to add metadata
    return loader.load()
