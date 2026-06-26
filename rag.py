from pathlib import Path

from lunaria_types import ProjectPath


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


def answer_with_lunaria(user_message: str) -> str:
    # Esta funcion queda como placeholder.
    # Despues aqui entraria el modelo de lenguaje y la busqueda real.
    system_prompt = load_system_prompt()
    context = build_context(user_message, "Pendiente conectar busqueda vectorial.")
    return f"{system_prompt}\n\n{context}"
