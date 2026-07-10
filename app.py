from rag import answer_with_lunaria


# Este seria el punto de entrada de la app.
# Segun mi hermano, app.py es como la puerta principal:
# aqui llegaria el mensaje de la usuaria y de aqui se manda al sistema RAG.


def main() -> None:
    # Prueba sencilla mientras todavia no esta conectada la interfaz con Chainlit.
    # En semana 8 ya permite escribir varios mensajes y revisar la recuperacion.
    print("Lunaria RAG - prueba de consola")
    print("Escribe 'salir' para terminar.\n")

    while True:
        user_message = input("Tu mensaje: ").strip()
        if user_message.lower() in ["salir", "exit", "q"]:
            print("Cerrando prueba de Lunaria.")
            break
        if not user_message:
            print("Escribe un mensaje para que Lunaria pueda buscar una senal.\n")
            continue

        response = answer_with_lunaria(user_message)
        print(f"\n{response}\n")


if __name__ == "__main__":
    main()
