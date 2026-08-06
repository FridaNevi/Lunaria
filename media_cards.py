import chainlit as cl
import httpx

from config import YOUTUBE_API_KEY
from lunaria_types import Recommendation

# Semana 12: antes cada recomendacion abria un panel lateral (display="side")
# apenas Lunaria mandaba el mensaje, sin que la persona usuaria pidiera nada.
# Ahora la recomendacion vive primero como mensaje normal, y solo se abre un
# popup si alguien hace clic en el boton ("Leer mas", "Escuchar", "Ver video").
# Por eso ahora se manda un solo CustomElement con display="inline": el mismo
# componente (RecommendationCard.jsx) decide que mostrar segun el tipo.


def fetch_itunes_track(query: str) -> dict | None:
    # iTunes Search API no pide API key. Le mandamos "titulo autor" y nos
    # regresa datos de la cancion: portada, nombre, artista, album y un
    # preview de 30 segundos.
    try:
        response = httpx.get(
            "https://itunes.apple.com/search",
            params={"term": query, "media": "music", "limit": 1},
            timeout=5,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return results[0] if results else None
    except Exception:
        # Si iTunes no responde, Lunaria sigue mandando el mensaje sin tarjeta.
        return None


def fetch_google_book(query: str) -> dict | None:
    # Google Books API tambien es publica. Nos interesa el "id" del volumen
    # (para el Embedded Viewer) y tambien portada, descripcion y un link
    # de respaldo para el boton "Ver en Google Books".
    try:
        response = httpx.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": query, "maxResults": 1},
            timeout=5,
        )
        response.raise_for_status()
        items = response.json().get("items", [])
        return items[0] if items else None
    except Exception:
        return None


def fetch_youtube_video(query: str) -> dict | None:
    # YouTube Data API v3 si pide API key (a diferencia de iTunes y Google
    # Books). Buscamos por relevancia, asi que el resultado puede cambiar
    # con el tiempo.
    if not YOUTUBE_API_KEY:
        return None
    try:
        response = httpx.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": 1,
                "key": YOUTUBE_API_KEY,
            },
            timeout=5,
        )
        response.raise_for_status()
        items = response.json().get("items", [])
        return items[0] if items else None
    except Exception:
        return None


def _book_props(recommendation: Recommendation) -> dict | None:
    book = fetch_google_book(f"{recommendation.title} {recommendation.author}")
    if not book:
        return None

    volume_info = book.get("volumeInfo", {})
    sale_info = book.get("saleInfo", {})
    image_links = volume_info.get("imageLinks", {})

    return {
        "contentType": "book",
        "title": recommendation.title,
        "author": recommendation.author,
        "description": volume_info.get("description") or recommendation.description,
        "volumeId": book.get("id"),
        "coverUrl": image_links.get("thumbnail", "").replace("http://", "https://"),
        "externalUrl": sale_info.get("buyLink") or volume_info.get("infoLink", ""),
    }


def _music_props(recommendation: Recommendation) -> dict | None:
    track = fetch_itunes_track(f"{recommendation.title} {recommendation.author}")
    if not track:
        return None

    return {
        "contentType": "music",
        "title": track.get("trackName", recommendation.title),
        "author": track.get("artistName", recommendation.author),
        "description": recommendation.description,
        "albumName": track.get("collectionName", ""),
        "coverUrl": track.get("artworkUrl100", "").replace("100x100", "400x400"),
        "previewUrl": track.get("previewUrl"),
        "externalUrl": track.get("trackViewUrl", ""),
    }


def _video_props(recommendation: Recommendation) -> dict | None:
    # Primero intenta traer algo dinamico de YouTube. Si no hay
    # YOUTUBE_API_KEY, o la busqueda falla, usa el link fijo que quedo
    # guardado en el Observatorio.
    # Si el video ya viene de una busqueda externa (search_external), no
    # se vuelve a buscar: ya se encontro el video exacto una vez, y buscar
    # de nuevo con "titulo descripcion" puede traer algo totalmente distinto.
    video = None if recommendation.mode == "externo" else fetch_youtube_video(
        f"{recommendation.title} {recommendation.description}"
    )

    if video:
        snippet = video.get("snippet", {})
        return {
            "contentType": "video",
            "title": snippet.get("title", recommendation.title),
            "author": recommendation.author,
            "description": snippet.get("description") or recommendation.description,
            "videoId": video.get("id", {}).get("videoId", ""),
            "channelTitle": snippet.get("channelTitle", ""),
            "coverUrl": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        }

    if not recommendation.source_url:
        return None

    # Respaldo: el link fijo del Observatorio. Extrae el id del video del
    # link de YouTube para poder incrustarlo igual en el modal.
    video_id = recommendation.source_url.split("v=")[-1] if "v=" in recommendation.source_url else ""
    if not video_id:
        return None

    return {
        "contentType": "video",
        "title": recommendation.title,
        "author": recommendation.author,
        "description": recommendation.description,
        "videoId": video_id,
        "channelTitle": recommendation.author,
        "coverUrl": "",
    }


def build_media_elements(recommendation: Recommendation) -> list:
    # Segun el tipo de recomendacion, arma los props que le corresponden.
    # Si la busqueda externa falla o no hay coincidencia, regresa una lista
    # vacia: el mensaje de Lunaria se manda igual, solo que sin tarjeta.
    builders = {
        "music": _music_props,
        "book": _book_props,
        "video": _video_props,
    }
    builder = builders.get(recommendation.content_type)
    if not builder:
        return []

    props = builder(recommendation)
    if not props:
        return []

    return [cl.CustomElement(name="RecommendationCard", display="inline", props=props)]


def search_external(user_message: str) -> Recommendation | None:
    # Cuando el Observatorio no tiene nada que ofrecer, esta funcion busca
    # en vivo con el mensaje tal cual lo escribio la persona: primero en
    # YouTube, despues en Google Books, y al final en Apple Music (iTunes).
    # Se queda con el primer resultado que encuentre, en ese orden.
    video = fetch_youtube_video(user_message)
    if video:
        snippet = video.get("snippet", {})
        video_id = video.get("id", {}).get("videoId", "")
        return Recommendation(
            title=snippet.get("title", user_message),
            author=snippet.get("channelTitle", "YouTube"),
            content_type="video",
            mode="externo",
            phases=[],
            mood="resultado externo, no forma parte del Observatorio",
            description=snippet.get("description") or "Resultado encontrado en vivo en YouTube.",
            source_url=f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
        )

    book = fetch_google_book(user_message)
    if book:
        volume_info = book.get("volumeInfo", {})
        return Recommendation(
            title=volume_info.get("title", user_message),
            author=", ".join(volume_info.get("authors", [])) or "Autor desconocido",
            content_type="book",
            mode="externo",
            phases=[],
            mood="resultado externo, no forma parte del Observatorio",
            description=volume_info.get("description") or "Resultado encontrado en vivo en Google Books.",
        )

    track = fetch_itunes_track(user_message)
    if track:
        return Recommendation(
            title=track.get("trackName", user_message),
            author=track.get("artistName", "Apple Music"),
            content_type="music",
            mode="externo",
            phases=[],
            mood="resultado externo, no forma parte del Observatorio",
            description="Resultado encontrado en vivo en Apple Music.",
        )

    return None
