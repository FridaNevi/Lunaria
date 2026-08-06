import chainlit as cl

from media_cards import build_media_elements, search_external
from rag import generate_reply, retrieve_semantic_matches

# Semana 11: esta es la primera interfaz conversacional real de Lunaria.
# app.py sigue existiendo para pruebas de consola con traza tecnica,
# pero este archivo es el que de verdad se conecta a Chainlit.


@cl.on_chat_start
async def start() -> None:
    await cl.Message(
        content=(
            "Hola, soy Lunaria. Cuentame como te sientes o que estas buscando "
            "y te traigo una señal del Observatorio."
        )
    ).send()


@cl.on_message
async def main(message: cl.Message) -> None:
    # No se usa chat_with_lunaria() directo porque aqui tambien necesitamos
    # la recomendacion principal, para saber si hay que abrir una tarjeta
    # de cancion, un visor de libro o un video en el panel lateral.
    matches = retrieve_semantic_matches(message.content)
    recommendations = [match.recommendation for match in matches]

    # Si el Observatorio no tiene nada, se busca en vivo en YouTube,
    # Google Books o Apple Music antes de rendirse.
    if not recommendations:
        external_recommendation = search_external(message.content)
        if external_recommendation:
            recommendations = [external_recommendation]

    response = generate_reply(message.content, recommendations)

    elements = build_media_elements(recommendations[0]) if recommendations else []
    await cl.Message(content=response, elements=elements).send()
