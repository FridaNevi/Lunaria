from fastembed import TextEmbedding

from config import EMBEDDING_MODEL
from lunaria_types import Recommendation

# Un embedding es basicamente convertir texto en una lista de numeros
# que representa su significado. Dos textos parecidos en significado
# terminan con vectores parecidos, aunque no compartan las mismas palabras.
# Eso es lo que permite buscar por sentido y no solo por coincidencia literal.

_model: TextEmbedding | None = None


def get_embedding_model() -> TextEmbedding:
    # Cargar el modelo tarda unos segundos, asi que lo guardamos en _model
    # y lo reusamos en vez de recargarlo cada vez que se pide un embedding.
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=EMBEDDING_MODEL)
    return _model


def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    vector = next(model.embed([text]))
    return vector.tolist()


def build_searchable_text(recommendation: Recommendation) -> str:
    # Este es el texto que realmente se convierte en embedding.
    # Junta lo que importa para buscar por sentido: de que trata,
    # para que modo y fase sirve, y con que estado de animo encaja.
    return (
        f"{recommendation.title}. {recommendation.description} "
        f"Modo: {recommendation.mode}. Fase: {', '.join(recommendation.phases)}. "
        f"Estado de animo: {recommendation.mood}."
    )


def embed_recommendation(recommendation: Recommendation) -> list[float]:
    return embed_text(build_searchable_text(recommendation))