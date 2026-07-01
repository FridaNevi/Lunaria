# Lunaria - Avance Semana 7

## Repositorio del proyecto

El codigo fuente del proyecto se encuentra disponible en el siguiente enlace:

[Ver repositorio en GitHub](https://github.com/FridaNevi/Lunaria)

## Del Observatorio conceptual a una primera recuperacion funcional

## 1. Descripcion general

Este avance corresponde a la semana 7 del proyecto Lunaria. En la semana anterior se habia definido la estructura base del sistema RAG: el Observatorio, el prompt, los modos conversacionales y los enums principales.

Durante esta semana el objetivo fue pasar de una estructura conceptual a una primera version funcional. Lunaria ya no solo carga archivos del proyecto, sino que puede leer el Observatorio, convertir sus recomendaciones en datos organizados, buscar coincidencias segun el mensaje del usuario y construir una respuesta de prueba usando esa informacion.

Todavia no se implemento una base vectorial con embeddings. Esta semana se trabajo una recuperacion local sencilla, suficiente para probar el flujo antes de agregar mas complejidad.

## 2. Objetivo de la semana 7

La pregunta principal de esta etapa fue:

```txt
Como puede Lunaria empezar a recuperar informacion real de su Observatorio?
```

Para responderla, se trabajaron cuatro avances:

* Convertir las recomendaciones del Observatorio en objetos estructurados.
* Crear una busqueda local por palabras clave, modo y contenido.
* Simular una respuesta de Lunaria usando recomendaciones recuperadas.
* Actualizar el README para documentar el estado real del proyecto al cierre de la semana 7.

## 3. Avances tecnicos implementados

### 3.1 Lectura del Observatorio

El archivo `ingest.py` ahora mantiene la funcion para leer `observatorio/recomendaciones.md`, pero ya no se queda solamente con el texto completo.

La funcion `load_recommendations()` carga el Markdown, separa cada recomendacion y la convierte en una estructura que Python puede usar mejor.

Esto importa porque el sistema deja de tratar el Observatorio como una hoja de texto gigante y empieza a verlo como una coleccion de recomendaciones con campos.

### 3.2 Parsing de recomendaciones

Se agrego la funcion `parse_recommendation()`.

Su trabajo es tomar un bloque como este:

```txt
Titulo
Autor
Tipo
Modo
Fase
Estado de animo
Descripcion
```

Y convertirlo en una recomendacion estructurada.

Segun mi forma de entenderlo, este paso es como ordenar una libreta: el contenido ya existia, pero ahora cada dato tiene su lugar y puede ser encontrado con mas facilidad.

### 3.3 Modelo de datos Recommendation

En `lunaria_types.py` se agrego una clase `Recommendation`.

Esta clase guarda los campos principales de cada recomendacion:

* `title`
* `author`
* `content_type`
* `mode`
* `phases`
* `mood`
* `description`

Tambien incluye el metodo `as_context()`, que convierte la recomendacion en texto legible para que pueda usarse como contexto en el flujo RAG.

Esto ayuda a separar dos cosas:

* El Observatorio como archivo Markdown editable.
* Las recomendaciones como datos internos que Lunaria puede consultar.

### 3.4 Deteccion sencilla de modo

En `rag.py` se agrego `detect_mode()`.

Esta funcion revisa el mensaje del usuario y busca palabras relacionadas con los modos de Lunaria:

* Biblioteca: leer, libro, novela, autor.
* Frecuencia: musica, cancion, playlist.
* Chisme: chisme, contexto, dato curioso.
* Eclipse: triste, cansada, bloqueo, confusion.
* Caos: raro, inesperado, caos, sorprendeme.

No es una deteccion perfecta, pero sirve como primera version para probar el comportamiento del sistema sin depender todavia de un modelo externo.

### 3.5 Recuperacion local de recomendaciones

Tambien se agrego `retrieve_recommendations()`.

Esta funcion representa el primer intento real del RAG:

```txt
Mensaje del usuario
|
Detectar posible modo
|
Comparar contra recomendaciones del Observatorio
|
Ordenar por coincidencia
|
Regresar las mejores senales encontradas
```

La busqueda suma puntos cuando el mensaje coincide con el modo, el titulo, la fase, el estado de animo o la descripcion de una recomendacion.

Aunque no usa embeddings, ya permite probar el flujo completo de recuperacion.

## 4. Respuesta de prueba de Lunaria

La funcion `answer_with_lunaria()` tambien evoluciono.

Antes solo cargaba el prompt y mostraba un placeholder. Ahora:

1. Carga el prompt del sistema.
2. Recupera recomendaciones del Observatorio.
3. Construye contexto tecnico con el mensaje del usuario y la informacion recuperada.
4. Genera una respuesta simulada de Lunaria.

La respuesta todavia no viene de un modelo de lenguaje conectado. Es una respuesta armada desde Python para comprobar que la recuperacion funciona.

Esto es importante porque permite validar la logica antes de conectar Groq, Chainlit o una base vectorial.

## 5. Ampliacion del Observatorio

El archivo `observatorio/recomendaciones.md` tambien se amplio.

Ahora el Observatorio incluye senales para los cinco modos principales:

* Biblioteca
* Frecuencia
* Chisme
* Eclipse
* Caos

Esto permite probar que la deteccion de modo no se quede limitada solo a libros o apoyo emocional.

## 6. Estructura actual del proyecto

La estructura del proyecto al cierre de la semana 7 queda asi:

```txt
LunariaRAG/
|- app.py
|- ingest.py
|- rag.py
|- lunaria_types.py
|- requirements.txt
|- README.md
|- observatorio/
|  |- recomendaciones.md
|- prompts/
   |- lunaria_system.txt
```

## 7. Explicacion de archivos

### app.py

Es el punto de entrada de prueba.

Por ahora no levanta Chainlit. Sirve para ejecutar un mensaje de ejemplo y revisar en consola si Lunaria recupera informacion del Observatorio.

### ingest.py

Lee el Observatorio, separa recomendaciones y las convierte en objetos `Recommendation`.

Este archivo representa la preparacion de datos.

### rag.py

Contiene la logica principal del flujo RAG provisional:

* Cargar el prompt.
* Detectar modo.
* Puntuar recomendaciones.
* Recuperar coincidencias.
* Armar una respuesta de prueba.

### lunaria_types.py

Guarda enums y estructuras compartidas:

* Modos conversacionales.
* Fases lunares simbolicas.
* Tipos de recomendacion.
* Rutas del proyecto.
* Clase `Recommendation`.

### observatorio/recomendaciones.md

Es la base de conocimiento curada de Lunaria.

Se mantiene en Markdown porque todavia es facil de editar, leer y ampliar sin necesitar una base de datos real.

### prompts/lunaria_system.txt

Define la identidad de Lunaria, su tono, sus reglas y sus limites.

Funciona como la hoja de personaje del sistema conversacional.

## 8. Como probar el avance

Desde la carpeta del proyecto:

```powershell
python app.py
```

Tambien se puede probar directamente la lectura del Observatorio:

```powershell
python ingest.py
```

El resultado esperado de `ingest.py` es una lista de recomendaciones encontradas junto con su modo.

## 9. Estado actual del RAG

El sistema ya tiene una primera version del flujo:

```txt
Usuario escribe un mensaje
|
Lunaria detecta una intencion aproximada
|
Busca recomendaciones en el Observatorio
|
Construye contexto tecnico
|
Genera una respuesta de prueba
```

Lo que ya existe:

* Lectura del Observatorio.
* Parsing de recomendaciones.
* Modelo de datos para recomendaciones.
* Deteccion basica de modo.
* Busqueda local por coincidencias.
* Respuesta simulada con contexto recuperado.

Lo que todavia falta:

* Embeddings.
* Base vectorial.
* Conexion real con un modelo de lenguaje.
* Integracion con Chainlit.
* Mejor deteccion de intencion.
* Pruebas con mas mensajes reales.

## 10. Importancia del avance

La semana 7 es importante porque Lunaria deja de ser solamente una idea bien organizada y empieza a tener comportamiento funcional.

Aunque la recuperacion todavia es sencilla, ya existe el ciclo basico del sistema RAG:

```txt
leer -> estructurar -> buscar -> recuperar -> responder
```

Esto permite avanzar con mas seguridad hacia embeddings y una interfaz conversacional, porque ya se comprobo que la informacion del Observatorio puede entrar al flujo tecnico.

## 11. Proximos pasos

Los siguientes pasos recomendados son:

1. Agregar mas recomendaciones al Observatorio.
2. Normalizar mejor los campos de metadata.
3. Crear embeddings para cada recomendacion.
4. Guardar los embeddings en una base vectorial local.
5. Reemplazar la busqueda por palabras clave con busqueda semantica.
6. Conectar `answer_with_lunaria()` con un modelo de lenguaje.
7. Integrar el flujo con Chainlit.
8. Probar conversaciones reales por cada modo.
9. Ajustar el prompt segun errores y respuestas raras.

## 12. Conclusion

El avance de la semana 7 convierte la base tecnica de Lunaria en una primera version funcional.

El proyecto ya puede leer su Observatorio, interpretar recomendaciones, buscar coincidencias y construir una respuesta usando informacion recuperada.

Todavia no es el RAG final, pero ya tiene la forma principal del sistema. A partir de aqui, el siguiente salto natural es reemplazar la busqueda local por embeddings y conectar la respuesta con un modelo de lenguaje para que Lunaria pueda contestar con mas naturalidad sin perder el control sobre sus recomendaciones.
