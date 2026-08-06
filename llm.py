from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL

# Aqui es donde Lunaria deja de improvisar una respuesta armada a mano
# (format_lunaria_answer, en rag.py) y le pasa la posta a un modelo de
# lenguaje real. Groq no cobra por probar y responde rapido, por eso
# se eligio para esta primera conexion real.


def get_groq_client() -> Groq:
    return Groq(api_key=GROQ_API_KEY)


def generate_lunaria_reply(system_prompt: str, user_message: str, recovered_context: str) -> str:
    # El system_prompt le da la identidad a Lunaria (prompts/lunaria_system.txt).
    # El recovered_context es lo que ya encontro la busqueda semantica en el
    # Observatorio. El modelo solo debe recomendar con base en ese contexto.
    client = get_groq_client()
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "Informacion recuperada del Observatorio:\n"
                    f"{recovered_context}\n\n"
                    "Mensaje de la persona usuaria:\n"
                    f"{user_message}"
                ),
            },
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content