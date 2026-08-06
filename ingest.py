from pathlib import Path

from lunaria_types import ProjectPath, Recommendation


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
    # En semana 7 esto ya se usa como paso previo para convertir texto en objetos.
    sections = markdown_text.split("\n### ")
    return [
        section.strip()
        for section in sections
        if section.strip() and not section.strip().startswith("# Observatorio")
    ]


def _read_field(lines: list[str], field_name: str) -> str:
    # Funcion pequena para no repetir la misma busqueda de "Autor:", "Modo:", etc.
    # Si el campo no existe, regreso texto vacio para que el programa no se rompa.
    prefix = f"{field_name}:"
    for line in lines:
        if line.startswith(prefix):
            return line.replace(prefix, "", 1).strip()
    return ""


def normalize_field(value: str) -> str:
    # En semana 9 el Observatorio crecio, y a mano es facil que un campo
    # quede con mayusculas de mas o espacios raros. Esta funcion pareja
    # deja todo en minusculas y sin espacios sobrantes antes de comparar.
    return value.strip().lower()


def parse_recommendation(section: str) -> Recommendation:
    # Cada bloque del markdown empieza con el titulo y despues trae metadata.
    # Aqui convierto ese bloque en una Recommendation para poder buscar mejor.
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    title = lines[0].replace("###", "").strip()
    if not title:
        raise ValueError("Se encontro una seccion del Observatorio sin titulo.")

    # dict.fromkeys en vez de un set: quita fases repetidas pero conserva
    # el orden en el que quedaron escritas en el markdown.
    phases = list(
        dict.fromkeys(
            normalize_field(phase)
            for phase in _read_field(lines, "Fase").split(",")
            if phase.strip()
        )
    )

    recommendation = Recommendation(
        title=title,
        author=_read_field(lines, "Autor"),
        content_type=normalize_field(_read_field(lines, "Tipo")),
        mode=normalize_field(_read_field(lines, "Modo")),
        phases=phases,
        mood=_read_field(lines, "Estado de ánimo"),
        description=_read_field(lines, "Descripción"),
        # Campo opcional: solo las recomendaciones de video lo traen.
        source_url=_read_field(lines, "Video"),
    )

    if not recommendation.mode:
        raise ValueError(f"'{title}' no tiene Modo en el Observatorio.")
    if not recommendation.description:
        raise ValueError(f"'{title}' no tiene Descripción en el Observatorio.")

    return recommendation


def load_recommendations() -> list[Recommendation]:
    # Esta funcion ya seria la entrada limpia al Observatorio.
    # En lugar de regresar todo el markdown, regresa una lista de recomendaciones.
    markdown_text = load_observatorio()
    sections = split_recommendations(markdown_text)
    return [parse_recommendation(section) for section in sections]


def main() -> None:
    # Este main es una prueba simple para confirmar que el Observatorio se lee.
    # En semana 7 tambien confirma que las recomendaciones se pudieron parsear.
    recommendations = load_recommendations()
    print(f"Recomendaciones encontradas: {len(recommendations)}")
    for recommendation in recommendations:
        print(f"- {recommendation.title} ({recommendation.mode})")


if __name__ == "__main__":
    main()
