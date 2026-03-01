from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

_embeddings_instance = None


def get_embeddings() -> FastEmbedEmbeddings:
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = FastEmbedEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
        )
    return _embeddings_instance
