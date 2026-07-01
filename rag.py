from pathlib import Path

from ingest import load_recommendations
from lunaria_types import LunariaMode, ProjectPath, Recommendation


# RAG significa Retrieval Augmented Generation.
# Segun mi hermano, dicho menos intenso: primero busco informacion guardada
# y luego uso esa informacion para que la IA responda con mas contexto.


def load_system_prompt() -> str:
    # Este prompt es como la hoja de personaje de Lunaria:
    # le dice como hablar, que tono usar y que limites respetar.
    prompt_path = Path(ProjectPath.SYSTEM_PROMPT.value)
    return prompt_path.read_text(encoding="utf-8")


def build_context(user_message: str, recovered_text: str) -> str:
    # Aqui se juntaria lo que pidio la persona con lo que encontro el sistema.
    # Por ahora es una version sencilla para visualizar como se armaria.
    return (
        "Mensaje del usuario:\n"
        f"{user_message}\n\n"
        "Informacion recuperada del Observatorio:\n"
        f"{recovered_text}"
    )


def detect_mode(user_message: str) -> str | None:
    # Esta deteccion es intencionalmente sencilla.
    # Segun mi hermano, antes de meter IA para clasificar, conviene probar reglas claras.
    message = user_message.lower()
    mode_keywords = {
        LunariaMode.BIBLIOTECA.value: ["leer", "libro", "novela", "autor", "biblioteca"],
        LunariaMode.FRECUENCIA.value: ["musica", "música", "cancion", "canción", "playlist"],
        LunariaMode.CHISME.value: ["chisme", "contexto", "dato", "curioso", "historia detras"],
        LunariaMode.ECLIPSE.value: ["triste", "cansada", "cansado", "bloqueo", "confusion", "confusión"],
        LunariaMode.CAOS.value: ["raro", "inesperado", "caos", "sorprendeme", "sorpréndeme"],
    }

    for mode, keywords in mode_keywords.items():
        if any(keyword in message for keyword in keywords):
            return mode
    return None


def score_recommendation(user_message: str, recommendation: Recommendation) -> int:
    # Esta es una busqueda local basica, todavia no vectorial.
    # Suma puntos cuando el mensaje coincide con modo, fase, titulo o descripcion.
    message = user_message.lower()
    searchable_text = " ".join(
        [
            recommendation.title,
            recommendation.author,
            recommendation.content_type,
            recommendation.mode,
            " ".join(recommendation.phases),
            recommendation.mood,
            recommendation.description,
        ]
    ).lower()

    score = 0
    detected_mode = detect_mode(user_message)
    if detected_mode and detected_mode == recommendation.mode:
        score += 3
    if detected_mode == LunariaMode.BIBLIOTECA.value and recommendation.content_type == "book":
        score += 2

    emotional_keywords = ["triste", "tristeza", "bloqueo", "cansada", "cansado", "confusion", "confusión"]
    if any(keyword in message for keyword in emotional_keywords):
        if "eclipse" in recommendation.phases:
            score += 3
        if recommendation.content_type == "emotional":
            score += 2

    for word in message.replace(".", " ").replace(",", " ").split():
        if len(word) > 3 and word in searchable_text:
            score += 1

    return score


def retrieve_recommendations(user_message: str, limit: int = 2) -> list[Recommendation]:
    # Aqui empieza el R de RAG: recuperar informacion antes de responder.
    # Cuando haya embeddings, esta funcion puede cambiar sin tocar toda la app.
    recommendations = load_recommendations()
    ranked = sorted(
        recommendations,
        key=lambda recommendation: score_recommendation(user_message, recommendation),
        reverse=True,
    )
    return [
        recommendation
        for recommendation in ranked[:limit]
        if score_recommendation(user_message, recommendation) > 0
    ]


def format_lunaria_answer(user_message: str, recommendations: list[Recommendation]) -> str:
    # Mientras no esta conectado el modelo de lenguaje, esta funcion simula una respuesta.
    # La idea es probar si la recuperacion trae recomendaciones coherentes.
    if not recommendations:
        return (
            "Lunaria reviso el Observatorio y no encontro una recomendacion clara "
            "para esa peticion. Mejor no inventar estrellas donde todavia no hay mapa."
        )

    main_recommendation = recommendations[0]
    extra_context = ""
    if len(recommendations) > 1:
        extra_context = f"\n\nTambien podria mirar: {recommendations[1].title}."

    return (
        "Creo que esta senal del Observatorio encaja contigo:\n\n"
        f"{main_recommendation.title}, de {main_recommendation.author}.\n\n"
        f"Te la recomiendo porque {main_recommendation.description.lower()}"
        f"\n\nModo detectado: {main_recommendation.mode}."
        f"\nFase simbolica: {', '.join(main_recommendation.phases)}."
        f"{extra_context}"
    )


def answer_with_lunaria(user_message: str) -> str:
    # Semana 7: ya no responde solo con placeholder.
    # Primero recupera recomendaciones del Observatorio y despues arma una respuesta simple.
    system_prompt = load_system_prompt()
    recommendations = retrieve_recommendations(user_message)
    recovered_text = "\n\n---\n\n".join(
        recommendation.as_context() for recommendation in recommendations
    )
    context = build_context(
        user_message,
        recovered_text or "No se encontro informacion suficiente en el Observatorio.",
    )
    response = format_lunaria_answer(user_message, recommendations)
    return f"{response}\n\n---\nContexto tecnico usado:\n{context}\n\n---\nPrompt cargado:\n{system_prompt}"
