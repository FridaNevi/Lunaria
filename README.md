# Lunaria - Avance Semanas 9 a 12

## Repositorio del proyecto

El codigo fuente del proyecto se encuentra disponible en el siguiente enlace:

[Ver repositorio en GitHub](https://github.com/FridaNevi/Lunaria)

## De una recuperacion revisable a un sistema conversacional completo

## 1. Descripcion general

Este avance junta las semanas 9, 10, 11 y 12 del proyecto Lunaria. En la semana 8 el sistema ya recuperaba recomendaciones con puntaje y razones, pero seguia siendo una busqueda por palabras y una respuesta simulada.

En las semanas 9 a 11 se cerro casi todo lo que quedaba pendiente en la ruta original: se amplio el Observatorio, se agregaron embeddings locales, se monto una base vectorial con Qdrant, se conecto un modelo de lenguaje real con Groq y se construyo la primera interfaz conversacional con Chainlit. Con esto el proyecto dejo de ser un prototipo de consola: ya es un sistema RAG completo, de punta a punta.

La semana 12 iba a ser solo de entrega, sin cambios de codigo. No fue asi del todo: al usar la interfaz seguido para probarla, se me hicieron evidentes varias cosas que se veian genericas o que fallaban a medias (el panel lateral se sentia invasivo, el avatar de Lunaria parpadeaba en blanco antes de cada respuesta). Con ayuda de mi hermano les entre a esos detalles antes de la entrega final: quedan documentados en la seccion 3.10 y 3.11.

## 2. Objetivo de las semanas 9 a 12

La pregunta que guio las primeras tres semanas fue:

```txt
Como paso de una recuperacion por palabras a una recuperacion por significado,
y de una respuesta simulada a una conversacion real?
```

Para responderla, se trabajo en cuatro bloques:

* Semana 9: ampliar el Observatorio, normalizar sus campos e introducir embeddings locales.
* Semana 10: guardar esos embeddings en una base vectorial (Qdrant) y agregar pruebas simples.
* Semana 11: conectar una respuesta real con Groq e integrar Chainlit como interfaz conversacional.
* Semana 12: entregar, y de paso pulir lo que ya se sentia raro con la interfaz corriendo (panel lateral invasivo, avatar sin estilo antes de cada respuesta, cero animacion).

## 3. Avances tecnicos implementados

### 3.1 Observatorio ampliado y campos normalizados (semana 9)

El Observatorio (`observatorio/recomendaciones.md`) tenia muy poco contenido en los modos chisme, eclipse y caos: una sola recomendacion cada uno. Eso hacia dificil probar si la busqueda por significado realmente distinguia entre recomendaciones parecidas. Ahora cada modo tiene al menos dos o tres recomendaciones.

En `ingest.py` se agrego `normalize_field()`, que deja modo, tipo y fases en minusculas y sin espacios sobrantes antes de compararlos. `parse_recommendation()` tambien valida que cada bloque tenga titulo, modo y descripcion; si falta alguno, avisa con un error claro en vez de dejar pasar una recomendacion incompleta en silencio.

### 3.2 Embeddings locales con fastembed (semana 9)

En `embeddings.py` se agrego la primera version de embeddings del proyecto.

Un embedding es basicamente convertir un texto en una lista de numeros que representa su significado. Dos frases parecidas en significado (aunque no compartan palabras, como "estoy agotada" y "quiero bajar el ritmo") terminan con vectores parecidos. Eso es lo que permite buscar por sentido en vez de por coincidencia literal de palabras, que era la limitacion de `evaluate_recommendation()` en la semana 8.

Se eligio `fastembed` con el modelo `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` porque:

* Es multilingue, y el Observatorio esta en español.
* Corre local, sin pedir API key ni conexion a internet despues de la primera descarga.
* Es liviano (unos 220 MB), a diferencia de otras opciones que piden GPU.

### 3.3 Base vectorial con Qdrant (semana 10)

En `vector_store.py` se agrego la conexion con Qdrant.

Qdrant es la base vectorial: en vez de guardar el texto de cada recomendacion, guarda su embedding para poder compararlo por similitud de significado. `index_observatorio()` lee el Observatorio, genera el embedding de cada recomendacion y lo sube a la coleccion configurada en `COLLECTION_NAME`. `search_similar()` hace lo mismo con el mensaje de la persona usuaria y le pide a Qdrant las recomendaciones mas parecidas.

Qdrant necesita correr por separado (por ejemplo con Docker) y escuchar en la direccion de `QDRANT_URL`. Este proyecto no lo levanta automaticamente.

### 3.4 Recuperacion semantica con respaldo lexico (semana 10)

En `rag.py` se agrego `retrieve_semantic_matches()`.

Intenta primero la busqueda semantica en Qdrant. Si Qdrant no esta disponible (por ejemplo, en una maquina donde todavia no se levanto el contenedor), cae de vuelta a `retrieve_recommendation_matches()`, la busqueda lexica de la semana 8. Asi Lunaria nunca se queda sin ninguna recomendacion que ofrecer solo porque la base vectorial esta apagada.

### 3.5 Pruebas simples (semana 10)

Se agrego `test_rag.py` con pytest. Usa los mismos cinco mensajes de ejemplo que ya estaban en el README de la semana 8 (uno por cada modo) y confirma que:

* `detect_mode()` siga reconociendo los cinco modos.
* `retrieve_recommendations()` traiga una recomendacion del modo correcto para cada mensaje.
* Los puntajes de `retrieve_recommendation_matches()` queden ordenados de mayor a menor.
* `retrieve_semantic_matches()` no truene aunque Qdrant no este arriba.
* Un mensaje ambiguo ("hola") no rompa la recuperacion.

### 3.6 Conexion real con Groq (semana 11)

En `llm.py` se agrego `generate_lunaria_reply()`, que le manda a Groq el prompt de sistema (`prompts/lunaria_system.txt`), el contexto recuperado del Observatorio y el mensaje de la persona usuaria, y regresa la respuesta que escribe el modelo.

En `rag.py`, `generate_reply()` decide que camino tomar: si hay una `GROQ_API_KEY` configurada, intenta la respuesta real; si no hay llave, o si Groq falla por cualquier motivo, usa `format_lunaria_answer()` (la respuesta simulada de la semana 8) como respaldo. Esto se probo en desarrollo con la llave que ya estaba en `.env` y Groq respondio con un error de autenticacion (llave invalida o vencida): el sistema no se cayo, simplemente siguio respondiendo con la version simulada. Antes de usar el modelo real hay que renovar esa llave en [console.groq.com](https://console.groq.com).

### 3.7 Interfaz conversacional con Chainlit (semana 11)

Se agrego `chainlit_app.py`, la primera interfaz conversacional real del proyecto. Ya no es una prueba de consola: es una ventana de chat donde se puede escribir con Lunaria como se haria con cualquier asistente.

### 3.8 Separar salida tecnica de respuesta final (semana 11)

En la semana 8 quedo pendiente "separar mejor salida tecnica y respuesta final". Ahora `rag.py` tiene `generate_reply()` (respuesta real o simulada, sin traza) y `answer_with_lunaria()` (respuesta junto con traza de recuperacion y contexto, para revisar en consola con `app.py`). `chainlit_app.py` usa `retrieve_semantic_matches()` + `generate_reply()` directamente, en vez de una sola funcion combinada, porque tambien necesita la recomendacion principal para decidir que tarjeta mostrar (ver 3.9).

### 3.9 Tarjetas multimedia en el panel lateral (extra, semana 11)

Se agrego `media_cards.py` y una carpeta `public/elements/` con dos componentes propios de Chainlit (`SongCard.jsx` y `BookViewer.jsx`). La idea: cuando Lunaria recomienda algo, ademas del texto aparece un elemento interactivo que se abre en el panel lateral, igual que los Artifacts de Claude.

* **Musica**: `fetch_itunes_track()` busca en la iTunes Search API (sin API key) y regresa portada, nombre, artista y un preview de 30 segundos. Ese dato llena `SongCard.jsx`, que se muestra con `cl.CustomElement(..., display="side")`.
* **Libros**: `fetch_google_book()` busca en la Google Books API el volumen y su `id`. `BookViewer.jsx` carga el script de Google (`google.books.jsapi.js`) y dibuja el Google Books Embedded Viewer con ese `id`.
* **Video**: no hizo falta programar un componente nuevo para el reproductor. El elemento nativo `cl.Video` de Chainlit ya usa react-player por dentro. Lo que si es nuevo es que el video ya no es siempre el mismo link fijo: `fetch_youtube_video()` busca en vivo en la YouTube Data API v3 usando el titulo y la descripcion de la recomendacion, asi que puede traer un video en tendencia, uno de chisme, o lo que sea que este sonando hoy sobre ese tema. A diferencia de iTunes y Google Books, YouTube Data API v3 si pide una API key (`YOUTUBE_API_KEY` en `.env`, con cuota gratuita limitada). Si no hay llave configurada, o la busqueda no encuentra nada, se usa de respaldo el campo `Video:` fijo que quedo guardado en el Observatorio (el ejemplo de TED-Ed sobre las fases de la luna).

Si la busqueda externa falla (API caida, sin resultados, sin llave configurada, o -como paso en desarrollo con Google Books- se agota la cuota de la IP), `build_media_elements()` regresa una lista vacia o usa el respaldo disponible: el mensaje de Lunaria se manda igual, solo que sin tarjeta. Mismo criterio de respaldo que ya se uso con Qdrant y con Groq.

### 3.10 Sin panel lateral: tarjetas como popup (semana 12)

Usando la interfaz de la semana 11 me di cuenta de algo que no se nota hasta que uno la prueba seguido: el panel lateral se abria solo, apenas Lunaria mandaba el mensaje, sin que yo pidiera nada. Mi hermano me hizo ver que eso se siente invasivo, como si la app decidiera por mi que es lo que quiero ver antes de que termine de leer la respuesta.

Por eso `SongCard.jsx` y `BookViewer.jsx` (que eran dos componentes separados) se unieron en uno solo, `RecommendationCard.jsx`, en `public/elements/`. Ahora Lunaria manda el mensaje normal, con un botoncito chiquito abajo que dice "Escuchar", "Leer más" o "Ver video" segun el tipo de recomendacion, y solo si alguien le hace clic se abre un popup centrado con lo que corresponda adentro (el reproductor de iTunes, el visor de Google Books o el video de YouTube incrustado). `media_cards.py` sigue armando los mismos datos que antes, nada mas que ahora los manda con `display="inline"` en vez de `display="side"`.

### 3.11 Sistema de estilos propio y un bug de avatar que costó encontrar (semana 12)

Hasta la semana 11 Lunaria corria con el tema por defecto de Chainlit. Para que se sintiera como un observatorio nocturno de verdad, y no como un chatbot generico con otro nombre, arme una carpeta `public/styles/` con un archivo por responsabilidad (variables y colores, tema de fondo, tipografia, layout, header, mensajes, tarjetas, botones, formularios, iconos, animaciones, utilidades y responsive), todos importados desde `public/style.css`. Tambien agregue un `public/theme.json` para los colores base de Chainlit y un avatar propio en `public/avatars/lunaria.svg`: una luna creciente dorada sobre un fondo azul noche.

Ya con el sistema de estilos armado, note algo raro probando la app: justo antes de que llegara la respuesta de Lunaria, su avatar se veia como un circulo blanco liso, sin ningun estilo, y de repente aparecia la luna dorada de golpe. Le pregunte a mi hermano y entre los dos revisamos el CSS: el problema era que el estilo del avatar (el fondo oscuro y el anillo dorado) solo estaba puesto para cuando el mensaje ya tenia la clase `.ai-message`, pero el avatar se pinta un instante antes de que esa clase exista. La solucion fue quitarle esa dependencia al estilo del avatar y ponerle un fondo propio directo a la imagen, para que se vea bien desde el primer instante sin importar en que momento del mensaje se pinte.

Ya que estaba en el CSS tambien agregue animaciones chiquitas, nada exagerado: el avatar y el botoncito de la tarjeta ("Leer más" / "Escuchar" / "Ver video") aparecen con un fundido suave en vez de aparecer de golpe, y el cursor de "Lunaria esta escribiendo" ahora pulsa en dorado en vez de parpadear en blanco como viene por defecto.

## 4. Estado actual del proyecto

Al cierre de la semana 12, el flujo completo de Lunaria queda asi:

```txt
Usuario escribe un mensaje
|
Se genera el embedding del mensaje
|
Qdrant busca las recomendaciones mas parecidas en significado
   (si Qdrant no responde, se usa la busqueda lexica de respaldo)
|
Se arma el contexto con las recomendaciones recuperadas
|
Groq genera la respuesta final usando ese contexto
   (si no hay llave o Groq falla, se usa la respuesta simulada)
|
Chainlit muestra la respuesta en una conversacion real
```

Lo que ya existe:

* Lectura y parsing normalizado del Observatorio.
* Embeddings locales con fastembed.
* Base vectorial con Qdrant e indexado del Observatorio.
* Recuperacion semantica con respaldo lexico automatico.
* Pruebas simples con pytest.
* Conexion real con un modelo de lenguaje (Groq), con respaldo simulado.
* Interfaz conversacional con Chainlit.
* Salida tecnica y respuesta final separadas.
* Tarjetas interactivas como popup: cancion (iTunes), libro (Google Books) y video, con busqueda dinamica en YouTube (react-player nativo de Chainlit), unificadas en un solo componente (`RecommendationCard.jsx`).
* Sistema de estilos propio en `public/styles/` (tema oscuro, avatar, tarjetas, botones y animaciones sutiles), en vez del tema por defecto de Chainlit.

Lo que todavia falta, y ya no son piezas grandes sino ajustes finos:

* Poner una `GROQ_API_KEY` real en `.env` (todavia tiene el valor de ejemplo `tu_api_key`) para que la respuesta real quede activa.
* Poner una `YOUTUBE_API_KEY` real en `.env` para que el video sea dinamico en vez de usar siempre el link fijo del Observatorio.
* Levantar Qdrant (por ejemplo con Docker) antes de cada sesion de prueba.
* Confirmar que la cuota de la Google Books API no este agotada (en desarrollo se topo con un 429 por cuota de la IP compartida del entorno de pruebas).
* Probar con conversaciones reales mas largas, no solo mensajes sueltos.
* Mejorar la deteccion de intencion si aparecen mensajes ambiguos frecuentes.

## 5. Estructura actual del proyecto

La estructura del proyecto al cierre de la semana 12 queda asi:

```txt
LunariaRAG/
|- app.py
|- chainlit_app.py
|- config.py
|- embeddings.py
|- ingest.py
|- llm.py
|- media_cards.py
|- rag.py
|- vector_store.py
|- lunaria_types.py
|- test_rag.py
|- requirements.txt
|- README.md
|- chainlit.md
|- .chainlit/
|  |- config.toml
|- observatorio/
|  |- recomendaciones.md
|- prompts/
|  |- lunaria_system.txt
|- public/
   |- style.css
   |- theme.json
   |- avatars/
   |  |- lunaria.svg
   |- elements/
   |  |- RecommendationCard.jsx
   |- styles/
      |- variables.css
      |- theme.css
      |- typography.css
      |- layout.css
      |- sidebar.css
      |- header.css
      |- chat.css
      |- messages.css
      |- cards.css
      |- buttons.css
      |- forms.css
      |- icons.css
      |- animations.css
      |- utilities.css
      |- responsive.css
```

## 6. Explicacion de archivos

### app.py

Prueba de consola con traza tecnica. Usa `answer_with_lunaria()` para revisar que la recuperacion (ahora semantica) siga trayendo recomendaciones coherentes.

### chainlit_app.py

Interfaz conversacional real. Recupera y genera la respuesta sin traza tecnica, y adjunta la tarjeta multimedia de la recomendacion principal (cancion, libro o video) usando `media_cards.py`.

### config.py

Centraliza las variables de entorno (`GROQ_API_KEY`, `GROQ_MODEL`, `QDRANT_URL`, `COLLECTION_NAME`) y el nombre del modelo de embeddings, para no repetir `os.getenv()` en cada archivo.

### embeddings.py

Genera los embeddings de recomendaciones y mensajes con fastembed. Es la base de la busqueda semantica.

### ingest.py

Lee el Observatorio, separa recomendaciones, normaliza sus campos y las convierte en objetos `Recommendation`.

### llm.py

Le pide a Groq la respuesta final de Lunaria, usando el prompt de sistema y el contexto recuperado del Observatorio.

### media_cards.py

Busca en iTunes Search API y Google Books API, y arma los elementos de Chainlit (tarjeta de cancion, visor de libro o video) que se adjuntan al mensaje de `chainlit_app.py`.

### public/elements/RecommendationCard.jsx

Componente personalizado de Chainlit que reemplazo a `SongCard.jsx` y `BookViewer.jsx` en la semana 12. Muestra un botoncito bajo el mensaje de Lunaria y solo abre el popup con el contenido (cancion, libro o video) si alguien le hace clic, en vez de abrirse solo como pasaba con el panel lateral.

### public/styles/ y public/avatars/lunaria.svg

Sistema de estilos propio de la semana 12, un archivo CSS por responsabilidad (variables, tema, tipografia, layout, mensajes, tarjetas, botones, etc.), todos importados desde `public/style.css`. `lunaria.svg` es el avatar de Lunaria: una luna creciente dorada sobre fondo azul noche.

### rag.py

Contiene la logica principal del flujo RAG:

* Detectar modo.
* Recuperar por significado (con respaldo lexico).
* Generar la respuesta, real o simulada.
* Separar respuesta final de traza tecnica.

### vector_store.py

Conecta con Qdrant, indexa el Observatorio y busca las recomendaciones mas parecidas en significado a un mensaje.

### lunaria_types.py

Guarda enums y estructuras compartidas: modos, fases, tipos de recomendacion, rutas del proyecto y las clases `Recommendation` y `RecommendationMatch`.

### test_rag.py

Pruebas simples con pytest: un mensaje por cada modo, y una prueba de que la recuperacion semantica no se rompa sin Qdrant arriba.

### observatorio/recomendaciones.md

La base de conocimiento curada de Lunaria, ahora mas completa en chisme, eclipse y caos.

### prompts/lunaria_system.txt

Define la identidad de Lunaria, su tono, sus reglas y sus limites.

## 7. Como probar el avance

Desde la carpeta del proyecto, con el entorno virtual activado:

```powershell
pip install -r requirements.txt
```

Correr las pruebas simples:

```powershell
pytest
```

(Opcional, requiere Qdrant corriendo en la direccion de `QDRANT_URL`, por ejemplo con `docker run -p 6333:6333 qdrant/qdrant`) Indexar el Observatorio en la base vectorial:

```powershell
python vector_store.py
```

Probar en consola con traza tecnica:

```powershell
python app.py
```

Probar la interfaz conversacional real (con tarjetas de cancion, libro y video que se abren en un popup al hacer clic, ya no en el panel lateral):

```powershell
chainlit run chainlit_app.py -w
```

Si ya tenias otra terminal corriendo la app antes, ciérrala primero (o mata el proceso con `Get-Process chainlit | Stop-Process`) para no terminar con dos instancias abiertas a la vez confundiendo cual esta actualizada.

Si `GROQ_API_KEY` no esta configurada, o Groq devuelve un error, Lunaria sigue respondiendo con la version simulada de la semana 8: el sistema no se cae, solo pierde la generacion real hasta que se resuelva la llave. Lo mismo pasa si iTunes o Google Books no responden: el mensaje se manda igual, solo que sin tarjeta.

Para que el video sea dinamico (buscar en vivo en YouTube en vez de usar siempre el mismo link) hay que agregar `YOUTUBE_API_KEY` en `.env`, con una llave de la YouTube Data API v3 (se saca gratis en Google Cloud Console, habilitando esa API en un proyecto). La cuota gratuita es de 10,000 unidades al dia y cada busqueda cuesta 100, o sea, unas 100 busquedas diarias. Sin esa llave, Lunaria usa el link fijo que ya quedo guardado en el Observatorio.

## 8. Importancia de este cierre

Estas cuatro semanas son importantes porque conectan todas las piezas que estaban planeadas por separado: embeddings, base vectorial, modelo de lenguaje real e interfaz conversacional. Ya no son ideas para "mas adelante", son parte del sistema que corre hoy.

Tambien fue importante hacerlo con respaldos: si Qdrant no esta arriba, o si la llave de Groq no sirve, Lunaria igual responde. Un sistema que solo funciona cuando todo externo esta perfecto no sirve mucho para seguir probandolo en el dia a dia.

## 9. Ruta restante

Ya no queda codigo pendiente. Lo unico que falta es la entrega formal:

1. Confirmar que la `GROQ_API_KEY` este vigente si se quiere mostrar la respuesta real (no la simulada) en la demo.
2. Subir la version final al repositorio y entregarla.

## 10. Conclusion

Con las semanas 9, 10 y 11, Lunaria paso de ser un prototipo de consola con busqueda por palabras a un sistema RAG completo: busca por significado en una base vectorial, genera respuestas con un modelo de lenguaje real y se conversa con el desde una interfaz real, no desde una terminal.

La semana 12 iba a ser solo de entrega, pero termino siendo tambien la semana en la que Lunaria dejo de sentirse como una demo de Chainlit con otro nombre: sin panel lateral que se abre solo, con un avatar que no parpadea en blanco, y con las animaciones minimas que hacen que se sienta viva sin ser exagerada. El proyecto llega a la entrega con todas sus piezas conectadas, incluyendo lo que pasa cuando alguna de esas piezas externas (Qdrant, Groq, las APIs de musica/libros/video) no esta disponible.
