"""One agronomy knowledge base, loaded from the shared text files."""
import logging
from pathlib import Path
from threading import Lock

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
_KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "rag_standalone" / "knowledge"
_model = None
_index = None
_documents = None
_index_lock = Lock()


def _load_documents():
    documents = []
    if _KNOWLEDGE_DIR.is_dir():
        for path in sorted(_KNOWLEDGE_DIR.glob("*.txt")):
            text = path.read_text(encoding="utf-8").strip()
            if text:
                title = path.stem.split("_", 1)[-1].replace("_", " ")
                documents.append(f"{title}: {text}")
    return documents


def _get_index():
    global _model, _index, _documents

    if _index is not None:
        return _index

    with _index_lock:
        if _index is None:
            _documents = _load_documents()
            if not _documents:
                raise RuntimeError(f"No agronomy documents found in {_KNOWLEDGE_DIR}")
            _model = SentenceTransformer(_EMBEDDING_MODEL_NAME)
            embeddings = _model.encode(
                _documents,
                convert_to_numpy=True,
                normalize_embeddings=True,
            ).astype("float32")
            _index = faiss.IndexFlatIP(embeddings.shape[1])
            _index.add(np.ascontiguousarray(embeddings))
            logger.info("Agronomy RAG index initialized", extra={"documents": len(_documents)})

    return _index


def retrieve_knowledge(crop: str, npk: dict, query_context: str = "") -> list[str]:
    """Return the most relevant local agronomy documents for a recommendation or question."""
    documents = _load_documents() if _documents is None else _documents
    if not documents:
        return []
    query = (
        f"Crop: {crop}. Soil nutrients: N={npk.get('N', 'unknown')}, "
        f"P={npk.get('P', 'unknown')}, K={npk.get('K', 'unknown')}. {query_context}"
    )
    index = _get_index()
    query_embedding = _model.encode(
        [query], convert_to_numpy=True, normalize_embeddings=True
    ).astype("float32")
    _, indices = index.search(query_embedding, min(4, len(_documents)))
    return [_documents[item] for item in indices[0] if 0 <= item < len(_documents)]
