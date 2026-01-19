import uuid

from app.core.db.chroma import get_vectorstore


class RetrievalService:
    def __init__(self):
        """Wrapper around the project's vectorstore retriever.

        By default the retriever is configured to return the top-k candidates.
        """
        self.vectorstore = get_vectorstore()

    def retrieve(self, query: str, user_id: uuid.UUID):
        """Run a similarity search against the vector store.

        Args:
            query (str): the user query used to retrieve relevant documents.

        Returns:
            List[Document]: documents returned by the retriever.
        """
        retriever = get_vectorstore().as_retriever(
            search_kwargs={
                "k": 4,
                "filter": {
                    "user_id": str(user_id),
                },
            }
        )
        return retriever.invoke(query)
