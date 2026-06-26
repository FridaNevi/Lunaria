from pathlib import Path

from lunaria_types import ProjectPath


# Este archivo seria el que prepara el Observatorio.
# Mi forma de entenderlo: agarra el markdown con recomendaciones
# y lo deja listo para que Lunaria pueda buscar dentro de el.


def load_observatorio() -> str:
    # Segun mi hermano, Path es mas comodo que escribir rutas como texto normal,
    # porque Python entiende mejor donde esta el archivo.
    observatorio_path = Path(ProjectPath.OBSERVATORIO.value)
    return observatorio_path.read_text(encoding="utf-8")


def split_recommendations(markdown_text: str) -> list[str]:
    # Por ahora separo por titulos de recomendacion.
    # Mas adelante esto puede volverse mas fino para leer metadata como modo,
    # fase lunar, autor y tipo de contenido.
    sections = markdown_text.split("\n### ")
    return [section.strip() for section in sections if section.strip()]


def main() -> None:
    # Este main es una prueba simple para confirmar que el Observatorio se lee.
    # Todavia no crea embeddings; eso seria el siguiente paso tecnico.
    markdown_text = load_observatorio()
    recommendations = split_recommendations(markdown_text)
    print(f"Recomendaciones encontradas: {len(recommendations)}")


if __name__ == "__main__":
    main()
