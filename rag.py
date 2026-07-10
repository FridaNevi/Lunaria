from pathlib import Path

from ingest import load_recommendations
from lunaria_types import LunariaMode, ProjectPath, Recommendation, RecommendationMatch


# RAG significa Retrieval Augmented Generation.
# Segun mi hermano, dicho menos intenso: primero busco informacion guardada
# y luego uso esa informacion para que la IA responda con mas contexto.

STOP_WORDS = {
    "algo",
    "como",
    "dame",
    "para",
    "pero",
    "quiero",
    "una",
    "unas",
    "unos",
}


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


def evaluate_recommendation(user_message: str, recommendation: Recommendation) -> RecommendationMatch:
    # Esta es una busqueda local basica, todavia no vectorial.
    # Suma puntos cuando el mensaje coincide con modo, fase, titulo o descripcion.
    # En semana 8 tambien guarda razones para entender la decision.
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
    reasons = []
    detected_mode = detect_mode(user_message)
    if detected_mode and detected_mode == recommendation.mode:
        score += 3
        reasons.append(f"coincide con el modo {detected_mode}")
    if detected_mode == LunariaMode.BIBLIOTECA.value and recommendation.content_type == "book":
        score += 2
        reasons.append("la peticion parece de lectura y el tipo es book")

    emotional_keywords = ["triste", "tristeza", "bloqueo", "cansada", "cansado", "confusion", "confusión"]
    if any(keyword in message for keyword in emotional_keywords):
        if "eclipse" in recommendation.phases:
            score += 3
            reasons.append("el mensaje tiene carga emocional y la fase incluye eclipse")
        if recommendation.content_type == "emotional":
            score += 2
            reasons.append("el mensaje suena emocional y el tipo es emotional")

    for word in message.replace(".", " ").replace(",", " ").split():
        if len(word) > 3 and word not in STOP_WORDS and word in searchable_text:
            score += 1
            reasons.append(f"aparece la palabra '{word}' en la recomendacion")

    return RecommendationMatch(
        recommendation=recommendation,
        score=score,
        reasons=reasons,
    )


def score_recommendation(user_message: str, recommendation: Recommendation) -> int:
    # Mantengo esta funcion pequena porque todavia sirve para leer el ranking rapido.
    return evaluate_recommendation(user_message, recommendation).score


def retrieve_recommendation_matches(user_message: str, limit: int = 2) -> list[RecommendationMatch]:
    # Aqui empieza el R de RAG: recuperar informacion antes de responder.
    # Cuando haya embeddings, esta funcion puede cambiar sin tocar toda la app.
    recommendations = load_recommendations()
    matches = [evaluate_recommendation(user_message, recommendation) for recommendation in recommendations]
    ranked = sorted(
        matches,
        key=lambda match: match.score,
        reverse=True,
    )
    return [match for match in ranked[:limit] if match.score > 0]


def retrieve_recommendations(user_message: str, limit: int = 2) -> list[Recommendation]:
    # Esta funcion deja la salida anterior disponible:
    # otras partes pueden pedir solo recomendaciones, sin puntajes ni razones.
    return [
        match.recommendation
        for match in retrieve_recommendation_matches(user_message, limit)
    ]


def format_retrieval_trace(matches: list[RecommendationMatch]) -> str:
    # Esta traza no es para el usuario final.
    # Sirve para revisar en consola que la recuperacion tenga sentido.
    if not matches:
        return "No hubo coincidencias con puntaje mayor que cero."

    trace_lines = []
    for match in matches:
        reasons = "; ".join(match.reasons) if match.reasons else "sin razon registrada"
        trace_lines.append(
            f"- {match.recommendation.title} | puntaje: {match.score} | {reasons}"
        )
    return "\n".join(trace_lines)


def format_lunaria_answer(user_message: str, recommendations: list[Recommendation]) -> str:
    # Mientras no esta conectado el modelo de lenguaje, esta funcion simula una respuesta.
    # La idea es probar si la recuperacion trae recomendaciones coherentes.
    if not recommendations:
        return (
            "Lunaria reviso el Observatorio y no encontro una recomendacion clara "
            "para esa peticion. Mejor no inventar estrellas donde todavia no hay mapa."
        )

    main_recommendation = recommendations[0]
    description = main_recommendation.description
    if description.lower().startswith("una recomendación para cuando el usuario "):
        description = description.replace("Una recomendación para cuando el usuario ", "encaja con alguien que ", 1)
    elif description.lower().startswith("recomendación para cuando el usuario "):
        description = description.replace("Recomendación para cuando el usuario ", "encaja con alguien que ", 1)
    elif description.lower().startswith("una recomendación para cuando "):
        description = description.replace("Una recomendación para cuando ", "encaja con alguien que ", 1)
    elif description.lower().startswith("recomendación para cuando "):
        description = description.replace("Recomendación para cuando ", "encaja con alguien que ", 1)
    elif description.lower().startswith("una recomendación para "):
        description = description.replace("Una recomendación para ", "encaja con ", 1)
    elif description.lower().startswith("recomendación para "):
        description = description.replace("Recomendación para ", "encaja con ", 1)

    extra_context = ""
    if len(recommendations) > 1:
        extra_context = f"\n\nTambien podria mirar: {recommendations[1].title}."

    return (
        "Creo que esta senal del Observatorio encaja contigo:\n\n"
        f"{main_recommendation.title}, de {main_recommendation.author}.\n\n"
        f"Te la recomiendo porque {description.lower()}"
        f"\n\nModo detectado: {main_recommendation.mode}."
        f"\nFase simbolica: {', '.join(main_recommendation.phases)}."
        f"{extra_context}"
    )


def answer_with_lunaria(user_message: str) -> str:
    # Semana 8: sigue siendo una respuesta simulada, pero ahora deja ver
    # que coincidencias encontro y por que las eligio.
    system_prompt = load_system_prompt()
    matches = retrieve_recommendation_matches(user_message)
    recommendations = [match.recommendation for match in matches]
    recovered_text = "\n\n---\n\n".join(
        recommendation.as_context() for recommendation in recommendations
    )
    context = build_context(
        user_message,
        recovered_text or "No se encontro informacion suficiente en el Observatorio.",
    )
    trace = format_retrieval_trace(matches)
    response = format_lunaria_answer(user_message, recommendations)
    return (
        f"{response}\n\n"
        f"---\nTraza de recuperacion:\n{trace}\n\n"
        f"---\nContexto tecnico usado:\n{context}\n\n"
        f"---\nPrompt cargado:\n{system_prompt}"
    )
