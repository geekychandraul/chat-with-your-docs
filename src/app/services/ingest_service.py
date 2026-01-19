import hashlib
import uuid

from fastapi.exceptions import HTTPException

from app.core.db.chroma import get_vectorstore
from app.core.logging import get_logger
from app.models.chunking import DocumentChunk
from app.models.file_metadata import FileMetadata
from app.repositories.audit_repo import AuditRepository
from app.repositories.chunk_repo import ChunkRepository
from app.repositories.file_repo import FileRepository
from app.utils.chunking import chunk_documents
from app.utils.file_loader import load_documents

logger = get_logger(__name__)


class IngestService:
    """Service responsible for ingesting files into the system.

    Responsibilities:
      - compute a file hash
      - persist file metadata
      - split documents into chunks and persist them
      - create embeddings in the vector store
      - audit log ingestion events
    """

    def __init__(self, db):
        """Initialize repositories and vector store clients.

        Args:
            db: a database session/connection used by repositories.
        """
        self.db = db
        self.files = FileRepository(db)
        self.chunks = ChunkRepository(db)
        self.audit = AuditRepository(db)
        self.vs = get_vectorstore()

    async def ingest(self, file, user_id: uuid.UUID):
        """Ingest a single uploaded file.

        This method reads the uploaded file, calculates a SHA256 hash to
        deduplicate, stores or updates file metadata, chunks the document,
        creates embeddings in the vector store, and persists chunk records.

        Args:
            file: an uploaded file-like object (Starlette UploadFile)

        Returns:
            dict: status and file_id on success or duplicate status.

        Raises:
            HTTPException: with status code 500 when ingestion fails.
        """
        try:
            # Create file hash
            content = await file.read()
            file_hash = hashlib.sha256(content).hexdigest()
            logger.debug("File hash: %s", file_hash)
        except Exception as e:
            logger.exception("Error reading file: %s", e)

        try:
            logger.info("Ingesting file %s with hash %s", file.filename, file_hash)
            # Save file's metadata to db
            file_meta: FileMetadata | None = await self.files.get_by_hash(file_hash)
            if file_meta:
                # Handle Failed and duplicate file
                if file_meta.status != "failed":
                    logger.info("Duplicate file detected for %s", file.filename)
                    return {"status": "duplicate"}
                else:
                    file_meta.status = "processing"
            else:
                file_meta = FileMetadata(
                    filename=file.filename,
                    file_hash=file_hash,
                    status="processing",
                    user_id=user_id,
                )
            await self.files.save(file_meta)
            # Reload file stream
            file.file.seek(0)
            documents = load_documents(file)
            chunks = chunk_documents(documents)
            texts = [c.page_content for c in chunks]
            logger.info("Total number of chunks: %d", len(chunks))
            metadatas = [
                {
                    "file_id": str(file_meta.id),
                    "user_id": str(user_id),
                    **c.metadata,
                }
                for c in chunks
            ]
            print("metadatas", metadatas)
            # Create embedding in chroma
            ids = self.vs.add_texts(texts=texts, metadatas=metadatas)

            chunk_rows = [
                DocumentChunk(
                    file_id=file_meta.id,
                    chunk_index=i,
                    chroma_id=ids[i],
                )
                for i in range(len(ids))
            ]
            logger.info("Saving %d chunk rows to DB", len(chunk_rows))
            await self.chunks.save_all(chunk_rows)

            file_meta.status = "processed"
            await self.db.commit()

            await self.audit.log(
                "INGEST_SUCCESS", {"file_id": str(file_meta.id)}, user_id=user_id
            )
            return {"status": "ingested", "file_id": str(file_meta.id)}
        except Exception as e:
            file_meta.status = "failed"  # type: ignore
            await self.db.commit()
            await self.audit.log("INGEST_FAILED", {"error": str(e)}, user_id)
            logger.exception("Ingestion failed: %s", e)
            raise HTTPException(status_code=500, detail="Ingestion failed") from e
