from ingest import load_recommendations
from lunaria_types import LunariaMode
from rag import (
    detect_mode,
    retrieve_recommendation_matches,
    retrieve_recommendations,
    retrieve_semantic_matches,
)

# Semana 10: pruebas simples con los mismos mensajes de ejemplo que ya
# estaban en el README. La idea no es cubrir todos los casos posibles,
# sino confirmar que cada modo se sigue detectando igual que cuando se
# probaba a mano desde app.py.

MENSAJES_POR_MODO = {
    LunariaMode.BIBLIOTECA.value: "Quiero leer algo triste pero bonito.",
    LunariaMode.FRECUENCIA.value: "Dame musica para caminar como protagonista.",
    LunariaMode.CHISME.value: "Quiero un chisme cultural.",
    LunariaMode.ECLIPSE.value: "Estoy cansada y confundida.",
    LunariaMode.CAOS.value: "Sorprendeme con algo raro.",
}


def test_detect_mode_reconoce_los_cinco_modos():
    for modo_esperado, mensaje in MENSAJES_POR_MODO.items():
        assert detect_mode(mensaje) == modo_esperado


def test_retrieve_recommendations_trae_resultados_del_modo_correcto():
    for modo_esperado, mensaje in MENSAJES_POR_MODO.items():
        recomendaciones = retrieve_recommendations(mensaje)
        assert recomendaciones, f"no hubo recomendaciones para: {mensaje}"
        assert recomendaciones[0].mode == modo_esperado


def test_retrieve_recommendation_matches_ordena_de_mayor_a_menor_puntaje():
    matches = retrieve_recommendation_matches("Quiero leer algo triste pero bonito.")
    puntajes = [match.score for match in matches]
    assert puntajes == sorted(puntajes, reverse=True)


def test_mensaje_sin_pistas_claras_no_rompe_la_recuperacion():
    # Un mensaje ambiguo no deberia hacer explotar nada, aunque no traiga
    # una recomendacion clara.
    recomendaciones = retrieve_recommendations("hola")
    assert isinstance(recomendaciones, list)


def test_retrieve_semantic_matches_no_se_rompe_sin_qdrant_arriba():
    # No se asume que Qdrant este corriendo (necesita el contenedor levantado).
    # Aunque falle la conexion, esta funcion tiene que caer de vuelta a la
    # busqueda lexica en vez de lanzar una excepcion.
    matches = retrieve_semantic_matches("Quiero leer algo triste pero bonito.")
    assert matches
    assert matches[0].recommendation.mode == LunariaMode.BIBLIOTECA.value


def test_recomendacion_de_video_trae_source_url():
    # Extra semana 11: el campo "Video" del Observatorio es opcional,
    # solo lo usan las recomendaciones de tipo video.
    recomendaciones = load_recommendations()
    videos = [r for r in recomendaciones if r.content_type == "video"]
    assert videos, "no se encontro ninguna recomendacion de tipo video"
    assert videos[0].source_url.startswith("https://")


def test_recomendaciones_sin_video_quedan_con_source_url_vacio():
    recomendaciones = load_recommendations()
    sin_video = [r for r in recomendaciones if r.content_type != "video"]
    assert all(r.source_url == "" for r in sin_video)
