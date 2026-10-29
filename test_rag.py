import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "rag_standalone" / "knowledge"
VECTOR_DIR = BASE_DIR / "rag_standalone" / "vector_store"
INDEX_PATH = VECTOR_DIR / "index.faiss"
DOCUMENTS_PATH = VECTOR_DIR / "documents.json"
MODEL_NAME = "all-MiniLM-L6-v2"

_model = None
_index = None
_documents = None


def retrieve(query: str, k: int = 3) -> list[str]:
    """Return the k most relevant agronomy documents for a query."""
    global _model, _index, _documents

    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if k < 1:
        return []

    if _index is None:
        _model = SentenceTransformer(MODEL_NAME)
        if INDEX_PATH.exists() and DOCUMENTS_PATH.exists():
            _index = faiss.read_index(str(INDEX_PATH))
            _documents = json.loads(DOCUMENTS_PATH.read_text(encoding="utf-8"))
        else:
            _documents = [
                path.read_text(encoding="utf-8").strip()
                for path in sorted(KNOWLEDGE_DIR.glob("*.txt"))
            ]
            if not _documents:
                raise FileNotFoundError(f"No knowledge documents found in {KNOWLEDGE_DIR}")

            embeddings = _model.encode(
                _documents,
                convert_to_numpy=True,
                normalize_embeddings=True,
            ).astype("float32")

            VECTOR_DIR.mkdir(parents=True, exist_ok=True)
            _index = faiss.IndexFlatIP(embeddings.shape[1])
            _index.add(embeddings)
            faiss.write_index(_index, str(INDEX_PATH))
            DOCUMENTS_PATH.write_text(
                json.dumps(_documents, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    query_embedding = _model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")
    _, indices = _index.search(query_embedding, min(k, len(_documents)))
    return [_documents[index] for index in indices[0] if index >= 0]


if __name__ == "__main__":
    print(f"Index saved to: {INDEX_PATH}")
    print("\n--- Retrieval test ---")
    for number, document in enumerate(
        retrieve("How should I fix yellow leaves caused by low nitrogen?"), 1
    ):
        print(f"\n[{number}]\n{document}")
