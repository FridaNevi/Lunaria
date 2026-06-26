# Lunaria - Avance Semana 6

## Repositorio del proyecto

El código fuente del proyecto se encuentra disponible en el siguiente enlace:

[Ver repositorio en GitHub](https://github.com/FridaNevi/Lunaria)

## Construccion del Observatorio: estructura RAG, prompt, recomendaciones y enums

## 1. Descripcion general

Este avance corresponde a la semana 6 del proyecto Lunaria. Despues de haber trabajado previamente en el prototipo conversacional y en la identidad visual del personaje, esta etapa se enfoco en comenzar la estructura tecnica que permitira que Lunaria funcione como una asistente RAG con una personalidad propia, modos conversacionales y una base de recomendaciones curada.

El objetivo principal de este avance no fue construir una version final del sistema, sino definir las bases del proyecto para que Lunaria pueda evolucionar de un chatbot con personalidad a una experiencia conversacional mas completa, capaz de consultar su propio Observatorio antes de responder.

En esta etapa se trabajaron tres componentes principales:

* La estructura inicial del proyecto.
* El diseno del prompt base de Lunaria.
* La creacion de una primera base de recomendaciones.
* La definicion de enums para organizar modos, fases lunares, rutas y tipos de contenido.

## 2. Contexto del avance

En semanas anteriores, Lunaria ya habia sido definida como personaje y como propuesta visual. La semana 4 permitio comprobar que era posible hacerla responder usando Chainlit y Groq. La semana 5 se enfoco en presentar su identidad visual.

La semana 6 parte de esa base y busca responder una nueva pregunta:

```txt
Como puede Lunaria empezar a tener una memoria curada propia?
```

Para responder esto, se planteo una version mas estructurada del sistema. En lugar de depender unicamente del conocimiento general del modelo de lenguaje, Lunaria comenzara a consultar una base de recomendaciones llamada Observatorio.

El Observatorio funcionara como una fuente de conocimiento interna donde se almacenaran libros, canciones, playlists, datos culturales y recomendaciones emocionales organizadas segun los modos de conversacion de Lunaria.

## 3. Concepto del Observatorio

El Observatorio es la base de conocimiento curada de Lunaria.

Su funcion es guardar recomendaciones que la asistente pueda consultar antes de responder. Esto permite que Lunaria no invente recomendaciones de forma aleatoria, sino que base sus respuestas en una seleccion previamente definida y coherente con su personalidad.

El Observatorio no se plantea como una base de datos fria, sino como una coleccion organizada de senales, lecturas, canciones y referencias culturales.

Ejemplo conceptual:

```txt
Observatorio
|- Biblioteca
|  |- Libros recomendados
|- Frecuencia
|  |- Musica y playlists
|- Chisme
|  |- Datos culturales y contexto
|- Eclipse
|  |- Recomendaciones emocionales
|- Caos
   |- Recomendaciones inesperadas
```

Esta estructura permite que Lunaria responda de acuerdo con el estado emocional o intencion del usuario.

## 4. Modos conversacionales

Se definieron cinco modos principales para organizar la personalidad y las respuestas de Lunaria.

### Biblioteca

Modo enfocado en libros, lectura, autores e historias. Se activa cuando el usuario busca una recomendacion literaria o expresa ganas de leer algo.

### Frecuencia

Modo enfocado en musica, canciones, artistas o playlists. Se activa cuando el usuario busca acompanamiento sonoro para un momento especifico.

### Chisme

Modo enfocado en contexto cultural, datos curiosos, autores, artistas o historias detras de obras. Permite que Lunaria explique detalles culturales con un tono mas casual.

### Eclipse

Modo enfocado en momentos emocionalmente densos: tristeza, bloqueo, cansancio, confusion o crisis creativa. No busca motivar de forma exagerada, sino acompanar con recomendaciones suaves y especificas.

### Caos

Modo mas libre, inesperado y experimental. Sirve para recomendaciones raras, combinaciones poco obvias o respuestas mas espontaneas.

## 5. Pensamiento detras del prompt

El prompt de Lunaria se penso como una traduccion tecnica de su identidad de personaje.

No se trata unicamente de decirle al modelo "responde bonito", sino de definir reglas claras sobre como debe comportarse, que tono debe usar, que limites debe respetar y como debe integrar la informacion recuperada del Observatorio.

El prompt se construyo considerando cuatro necesidades:

1. Mantener la personalidad de Lunaria.
2. Responder siempre en espanol.
3. Evitar que el modelo invente recomendaciones.
4. Integrar los modos conversacionales dentro de una logica clara.

## 6. Primera base de recomendaciones

Para comenzar el Observatorio, se planteo una primera base de recomendaciones en formato Markdown.

El objetivo de usar Markdown es que sea facil de escribir, leer y modificar sin necesidad de una base de datos compleja desde el inicio.

Cada recomendacion incluye metadata basica:

```txt
Titulo
Autor
Tipo
Modo
Fase lunar
Estado de animo
Descripcion
```

Esta metadata permitira que, mas adelante, el sistema pueda recuperar recomendaciones de forma mas precisa segun lo que el usuario escriba.

## 7. Uso de enums

Se decidio utilizar enums para evitar depender de textos escritos manualmente dentro del codigo.

Los enums ayudan a controlar valores fijos como modos, fases lunares, tipos de recomendacion y rutas del sistema.

Por ejemplo:

```python
class LunariaMode(str, Enum):
    BIBLIOTECA = "biblioteca"
    FRECUENCIA = "frecuencia"
    CHISME = "chisme"
    ECLIPSE = "eclipse"
    CAOS = "caos"
```

El uso de enums no busca mejorar directamente la velocidad del sistema, sino su mantenibilidad. Ayuda a que las rutas y categorias esten controladas y evita errores por escribir mal una palabra.

## 8. Estructura propuesta del proyecto

La estructura inicial propuesta para esta etapa es la siguiente:

```txt
LunariaRAG/
|- app.py
|- ingest.py
|- rag.py
|- lunaria_types.py
|- .env
|- requirements.txt
|- observatorio/
|  |- recomendaciones.md
|- prompts/
   |- lunaria_system.txt
```

### app.py

Archivo principal de la interfaz conversacional con Chainlit.

### ingest.py

Archivo encargado de leer el Observatorio, separar recomendaciones, generar embeddings y guardarlos en una base vectorial.

### rag.py

Archivo encargado de recibir preguntas, buscar informacion relevante en el Observatorio y generar una respuesta usando el modelo de lenguaje.

### lunaria_types.py

Archivo donde se definen enums y tipos base del sistema.

### observatorio/recomendaciones.md

Primera base de recomendaciones curadas de Lunaria.

### prompts/lunaria_system.txt

Prompt base que define la personalidad y reglas de respuesta de Lunaria.

## 9. Flujo tecnico propuesto

El flujo general del sistema sera:

```txt
Usuario escribe un mensaje
|
Lunaria detecta intencion o modo
|
Busca recomendaciones relevantes en el Observatorio
|
Construye contexto para el modelo
|
Genera una respuesta con personalidad
|
Muestra la recomendacion y la razon por la que encaja
```

## 10. Relacion entre diseno e implementacion

Este avance conecta directamente la identidad visual y conceptual de Lunaria con su implementacion tecnica.

La identidad visual define como se ve Lunaria.
El prompt define como habla Lunaria.
El Observatorio define que sabe Lunaria.
Los enums definen como se organiza internamente Lunaria.

De esta forma, el proyecto no se limita a tener una interfaz visual, sino que empieza a construir una logica funcional coherente con el personaje.

## 11. Proximos pasos

Los siguientes pasos del proyecto son:

1. Implementar el archivo `ingest.py` para procesar el Observatorio.
2. Generar embeddings de las recomendaciones.
3. Guardar las recomendaciones en una base vectorial.
4. Construir `rag.py` para recuperar recomendaciones relevantes.
5. Conectar el sistema RAG con Chainlit.
6. Probar los cinco modos conversacionales.
7. Ajustar el prompt segun las respuestas reales de Lunaria.
8. Documentar errores, limites y mejoras.

## 12. Conclusion

El avance de la semana 6 representa el inicio de una nueva etapa para Lunaria.

Despues de haber definido su personalidad, su primera interfaz y su identidad visual, este avance establece las bases para que Lunaria tenga una memoria curada propia.

El Observatorio permitira que sus recomendaciones no dependan unicamente del conocimiento general del modelo, sino de una seleccion intencional de libros, musica, referencias culturales y estados emocionales.

La creacion del prompt, la organizacion de recomendaciones y el uso de enums son pasos iniciales importantes para convertir a Lunaria en una experiencia conversacional mas solida, coherente y escalable.
