from app.core.db.chroma import get_vectorstore


class RetrievalService:
    def __init__(self):
        """Wrapper around the project's vectorstore retriever.

        By default the retriever is configured to return the top-k candidates.
        """
        self.retriever = get_vectorstore().as_retriever(search_kwargs={"k": 4})

    def retrieve(self, query: str):
        """Run a similarity search against the vector store.

        Args:
            query (str): the user query used to retrieve relevant documents.

        Returns:
            List[Document]: documents returned by the retriever.
        """
        return self.retriever.invoke(query)
