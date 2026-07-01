from rag import answer_with_lunaria


# Este seria el punto de entrada de la app.
# Segun mi hermano, app.py es como la puerta principal:
# aqui llegaria el mensaje de la usuaria y de aqui se manda al sistema RAG.


def main() -> None:
    # Prueba sencilla mientras todavia no esta conectada la interfaz con Chainlit.
    # En semana 7 ya sirve para revisar si Lunaria recupera algo del Observatorio.
    user_message = "Quiero leer algo triste pero bonito."
    response = answer_with_lunaria(user_message)
    print(response)


if __name__ == "__main__":
    main()
