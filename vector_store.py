from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from config import COLLECTION_NAME, QDRANT_URL
from embeddings import embed_recommendation, embed_text
from ingest import load_recommendations
from lunaria_types import Recommendation, RecommendationMatch

# Qdrant es la base vectorial. En vez de guardar el texto de cada
# recomendacion, guarda su embedding para poder compararlo por similitud
# de significado en lugar de comparar palabra por palabra como en rag.py.

VECTOR_SIZE = 384


def get_client() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL)


def ensure_collection(client: QdrantClient) -> None:
    # Solo crea la coleccion la primera vez. Si ya existe, no hay que tocarla.
    if client.collection_exists(COLLECTION_NAME):
        return
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )


def _recommendation_to_payload(recommendation: Recommendation) -> dict:
    # El payload es lo que Qdrant guarda junto al vector.
    # Aqui es la recomendacion completa, para poder reconstruirla despues
    # sin tener que volver a leer el Observatorio en cada busqueda.
    return {
        "title": recommendation.title,
        "author": recommendation.author,
        "content_type": recommendation.content_type,
        "mode": recommendation.mode,
        "phases": recommendation.phases,
        "mood": recommendation.mood,
        "description": recommendation.description,
    }


def _payload_to_recommendation(payload: dict) -> Recommendation:
    return Recommendation(
        title=payload["title"],
        author=payload["author"],
        content_type=payload["content_type"],
        mode=payload["mode"],
        phases=payload["phases"],
        mood=payload["mood"],
        description=payload["description"],
    )


def index_observatorio() -> int:
    # Esta funcion (re)llena la coleccion de Qdrant con el Observatorio actual.
    # Se puede correr de nuevo cada vez que se agreguen recomendaciones nuevas.
    client = get_client()
    ensure_collection(client)
    recommendations = load_recommendations()
    points = [
        PointStruct(
            id=index,
            vector=embed_recommendation(recommendation),
            payload=_recommendation_to_payload(recommendation),
        )
        for index, recommendation in enumerate(recommendations)
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points)


def search_similar(user_message: str, limit: int = 2) -> list[RecommendationMatch]:
    # Este es el reemplazo semantico de retrieve_recommendation_matches:
    # en vez de sumar puntos por palabras iguales, compara el significado
    # del mensaje contra el significado de cada recomendacion ya indexada.
    client = get_client()
    ensure_collection(client)
    query_vector = embed_text(user_message)
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
    ).points

    return [
        RecommendationMatch(
            recommendation=_payload_to_recommendation(point.payload),
            score=point.score,
            reasons=[f"similitud semantica de {point.score:.2f} con el mensaje"],
        )
        for point in results
    ]


def main() -> None:
    # Prueba simple para confirmar que Qdrant esta arriba y que el
    # Observatorio se puede indexar. Requiere Qdrant corriendo en QDRANT_URL.
    total = index_observatorio()
    print(f"Se indexaron {total} recomendaciones en la coleccion '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()