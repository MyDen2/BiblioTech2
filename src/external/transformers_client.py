from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None


def get_embedding_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def encode_text(text: str) -> list[float]:
    model = get_embedding_model()
    vector = model.encode(text)

    return vector.tolist()