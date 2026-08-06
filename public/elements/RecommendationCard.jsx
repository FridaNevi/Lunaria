import { useEffect, useRef, useState } from "react"

// Semana 12: un solo componente para las tres cosas que antes eran
// SongCard.jsx, BookViewer.jsx y cl.Video. En vez de abrir un panel
// lateral solo, ahora Lunaria manda el mensaje normal y este componente
// se ve como un boton chiquito ("Leer mas", "Escuchar", "Ver video").
// Solo al hacer clic se abre el popup, y el popup decide que mostrar
// adentro segun contentType.

const ACTION_LABEL = {
  book: "Leer más",
  music: "Escuchar",
  video: "Ver video",
  movie: "Ver detalles",
  series: "Ver detalles",
}

export default function RecommendationCard() {
  const [open, setOpen] = useState(false)
  const bookViewerRef = useRef(null)

  // Cerrar con ESC, y no dejar que el chat se mueva de scroll detras
  // del popup mientras esta abierto.
  useEffect(() => {
    if (!open) return

    function onKeyDown(event) {
      if (event.key === "Escape") setOpen(false)
    }

    document.addEventListener("keydown", onKeyDown)
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = "hidden"

    return () => {
      document.removeEventListener("keydown", onKeyDown)
      document.body.style.overflow = previousOverflow
    }
  }, [open])

  // El visor de Google Books solo se carga cuando el popup de un libro
  // esta abierto, igual que hacia el BookViewer.jsx original.
  useEffect(() => {
    if (!open || props.contentType !== "book" || !props.volumeId) return

    function initViewer() {
      if (!bookViewerRef.current) return
      const viewer = new window.google.books.DefaultViewer(bookViewerRef.current)
      viewer.load(props.volumeId)
    }

    if (window.google && window.google.books) {
      window.google.books.setOnLoadCallback(initViewer)
      return
    }

    const script = document.createElement("script")
    script.src = "https://www.google.com/books/jsapi.js"
    script.onload = () => {
      window.google.books.load()
      window.google.books.setOnLoadCallback(initViewer)
    }
    document.body.appendChild(script)
  }, [open])

  const label = ACTION_LABEL[props.contentType] || "Ver más"

  return (
    <>
      <button
        type="button"
        className="lunaria-open-trigger"
        onClick={() => setOpen(true)}
      >
        🌙 {label}
      </button>

      {open && (
        <div
          className="lunaria-modal-overlay"
          onClick={(event) => {
            if (event.target === event.currentTarget) setOpen(false)
          }}
        >
          <div className="lunaria-modal" role="dialog" aria-modal="true">
            <button
              type="button"
              className="lunaria-modal-close"
              onClick={() => setOpen(false)}
              aria-label="Cerrar"
            >
              ✕
            </button>

            <h2 className="lunaria-modal-title">{props.title}</h2>
            {props.author && (
              <p className="lunaria-modal-subtitle">{props.author}</p>
            )}

            {props.contentType === "book" && (
              <div className="lunaria-modal-body">
                {props.coverUrl && (
                  <img
                    src={props.coverUrl}
                    alt={props.title}
                    className="lunaria-modal-cover"
                  />
                )}
                <p className="lunaria-modal-description">{props.description}</p>
                {props.volumeId && (
                  <div ref={bookViewerRef} className="lunaria-book-viewer" />
                )}
                {props.externalUrl && (
                  <a
                    href={props.externalUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="lunaria-modal-external"
                  >
                    Ver en Google Books
                  </a>
                )}
              </div>
            )}

            {props.contentType === "music" && (
              <div className="lunaria-modal-body">
                {props.coverUrl && (
                  <img
                    src={props.coverUrl}
                    alt={props.title}
                    className="lunaria-modal-cover lunaria-modal-cover-square"
                  />
                )}
                {props.albumName && (
                  <p className="lunaria-modal-meta">Álbum: {props.albumName}</p>
                )}
                {props.previewUrl && (
                  <audio controls src={props.previewUrl} className="lunaria-modal-audio">
                    Tu navegador no soporta audio.
                  </audio>
                )}
                {props.externalUrl && (
                  <a
                    href={props.externalUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="lunaria-modal-external"
                  >
                    Escuchar en iTunes
                  </a>
                )}
              </div>
            )}

            {props.contentType === "video" && (
              <div className="lunaria-modal-body">
                {props.videoId && (
                  <div className="lunaria-modal-video">
                    <iframe
                      src={`https://www.youtube.com/embed/${props.videoId}`}
                      title={props.title}
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    />
                  </div>
                )}
                {props.channelTitle && (
                  <p className="lunaria-modal-meta">Canal: {props.channelTitle}</p>
                )}
                <p className="lunaria-modal-description">{props.description}</p>
              </div>
            )}

            {(props.contentType === "movie" || props.contentType === "series") && (
              <div className="lunaria-modal-body">
                {props.coverUrl && (
                  <img
                    src={props.coverUrl}
                    alt={props.title}
                    className="lunaria-modal-cover"
                  />
                )}
                <p className="lunaria-modal-meta">
                  {[props.year, props.duration].filter(Boolean).join(" · ")}
                </p>
                <p className="lunaria-modal-description">{props.description}</p>
                {props.externalUrl && (
                  <a
                    href={props.externalUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="lunaria-modal-external"
                  >
                    Ver más
                  </a>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}
