# Lunaria - Avance Semana 8

## Repositorio del proyecto

El codigo fuente del proyecto se encuentra disponible en el siguiente enlace:

[Ver repositorio en GitHub](https://github.com/FridaNevi/Lunaria)

## De una recuperacion funcional a una recuperacion revisable

## 1. Descripcion general

Este avance corresponde a la semana 8 del proyecto Lunaria. En la semana 7 el sistema ya podia leer el Observatorio, convertir recomendaciones en datos estructurados, buscar coincidencias y construir una respuesta de prueba.

Durante esta semana el objetivo no fue volver el proyecto mucho mas avanzado de golpe, sino hacer que la recuperacion sea mas facil de probar y revisar. Lunaria ahora no solo regresa una recomendacion, tambien muestra una traza tecnica sencilla con el puntaje y las razones por las que esa recomendacion fue elegida.

Todavia no se implementaron embeddings, base vectorial, Chainlit ni conexion real con un modelo de lenguaje. Esas partes siguen pendientes porque el proyecto todavia necesita varias semanas mas de construccion, pruebas y ajuste.

## 2. Objetivo de la semana 8

La pregunta principal de esta etapa fue:

```txt
Como puedo saber si Lunaria esta recuperando recomendaciones de forma coherente?
```

Para responderla, se trabajaron cuatro avances:

* Agregar una estructura para guardar coincidencias recuperadas.
* Registrar puntajes y razones durante la recuperacion.
* Crear una traza tecnica legible para revisar el ranking.
* Convertir `app.py` en una prueba de consola interactiva.

## 3. Avances tecnicos implementados

### 3.1 RecommendationMatch

En `lunaria_types.py` se agrego la clase `RecommendationMatch`.

Esta clase guarda tres cosas:

* La recomendacion recuperada.
* El puntaje que obtuvo.
* Las razones por las que sumo puntos.

Esto ayuda a revisar el comportamiento del sistema sin depender todavia de una interfaz visual o una base vectorial.

### 3.2 Evaluacion de recomendaciones

En `rag.py` se agrego `evaluate_recommendation()`.

Antes la funcion principal solo calculaba un numero. Ahora la evaluacion tambien guarda explicaciones como:

```txt
coincide con el modo biblioteca
el mensaje tiene carga emocional y la fase incluye eclipse
aparece la palabra 'triste' en la recomendacion
```

No es una explicacion perfecta, pero sirve para detectar si el sistema esta tomando decisiones razonables o si esta recuperando contenido por coincidencias muy debiles.

### 3.3 Recuperacion con trazas

Tambien se agrego `retrieve_recommendation_matches()`.

Esta funcion recupera recomendaciones igual que antes, pero ahora regresa coincidencias completas con puntaje y razones.

El flujo queda asi:

```txt
Mensaje del usuario
|
Detectar modo aproximado
|
Evaluar cada recomendacion
|
Guardar puntaje y razones
|
Ordenar coincidencias
|
Regresar las mejores senales
```

### 3.4 Compatibilidad con la version anterior

La funcion `retrieve_recommendations()` se conserva.

Esto importa porque permite que otras partes del proyecto sigan pidiendo solo recomendaciones, sin preocuparse por los puntajes. La version con trazas queda disponible para pruebas y revision tecnica.

### 3.5 Prueba de consola interactiva

`app.py` ya no usa solamente un mensaje fijo.

Ahora permite escribir varios mensajes desde la consola:

```txt
Tu mensaje: quiero leer algo triste
Tu mensaje: dame musica para caminar
Tu mensaje: salir
```

Esto hace mas facil probar distintos modos sin editar el codigo cada vez.

## 4. Estado actual del proyecto

Al cierre de la semana 8, Lunaria tiene un flujo RAG local y provisional:

```txt
Usuario escribe un mensaje
|
Lunaria detecta una intencion aproximada
|
Busca recomendaciones en el Observatorio
|
Asigna puntajes y razones
|
Construye contexto tecnico
|
Genera una respuesta simulada
```

Lo que ya existe:

* Lectura del Observatorio.
* Parsing de recomendaciones.
* Modelo de datos `Recommendation`.
* Modelo de coincidencias `RecommendationMatch`.
* Deteccion basica de modo.
* Busqueda local por coincidencias.
* Puntajes de recuperacion.
* Traza tecnica de recuperacion.
* Respuesta simulada con contexto recuperado.
* Prueba de consola interactiva.

Lo que todavia falta:

* Embeddings.
* Base vectorial local.
* Conexion real con un modelo de lenguaje.
* Integracion con Chainlit.
* Mejor deteccion de intencion.
* Mas recomendaciones en el Observatorio.
* Pruebas con conversaciones reales.
* Separar mejor salida tecnica y respuesta final.

## 5. Estructura actual del proyecto

La estructura del proyecto al cierre de la semana 8 queda asi:

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

## 6. Explicacion de archivos

### app.py

Es el punto de entrada de prueba.

Por ahora no levanta Chainlit. Sirve para escribir mensajes desde consola y revisar si Lunaria recupera informacion coherente del Observatorio.

### ingest.py

Lee el Observatorio, separa recomendaciones y las convierte en objetos `Recommendation`.

Este archivo representa la preparacion de datos.

### rag.py

Contiene la logica principal del flujo RAG provisional:

* Cargar el prompt.
* Detectar modo.
* Evaluar recomendaciones.
* Puntuar coincidencias.
* Registrar razones de recuperacion.
* Armar una respuesta de prueba.

### lunaria_types.py

Guarda enums y estructuras compartidas:

* Modos conversacionales.
* Fases lunares simbolicas.
* Tipos de recomendacion.
* Rutas del proyecto.
* Clase `Recommendation`.
* Clase `RecommendationMatch`.

### observatorio/recomendaciones.md

Es la base de conocimiento curada de Lunaria.

Se mantiene en Markdown porque todavia es facil de editar, leer y ampliar sin necesitar una base de datos real.

### prompts/lunaria_system.txt

Define la identidad de Lunaria, su tono, sus reglas y sus limites.

Funciona como la hoja de personaje del sistema conversacional.

## 7. Como probar el avance

Desde la carpeta del proyecto:

```powershell
python app.py
```

Despues se pueden escribir mensajes como:

```txt
Quiero leer algo triste pero bonito.
Dame musica para caminar como protagonista.
Quiero un chisme cultural.
Estoy cansada y confundida.
Sorprendeme con algo raro.
```

Para cerrar la prueba:

```txt
salir
```

Tambien se puede probar directamente la lectura del Observatorio:

```powershell
python ingest.py
```

El resultado esperado de `ingest.py` es una lista de recomendaciones encontradas junto con su modo.

## 8. Importancia del avance

La semana 8 es importante porque hace que el sistema sea mas revisable.

Antes Lunaria podia recuperar recomendaciones, pero no era tan claro por que una recomendacion quedaba arriba de otra. Ahora la traza permite observar el puntaje y las razones de cada coincidencia.

Esto todavia no reemplaza una evaluacion real, pero ayuda a encontrar errores antes de agregar embeddings o un modelo de lenguaje.

## 9. Ruta aproximada para las siguientes semanas

Como todavia quedan alrededor de seis semanas de trabajo, el proyecto puede avanzar por etapas:

1. Semana 9: ampliar el Observatorio y normalizar mejor los campos.
2. Semana 10: crear pruebas simples con mensajes esperados por cada modo.
3. Semana 11: introducir embeddings de forma local.
4. Semana 12: guardar y consultar una base vectorial pequena.
5. Semana 13: conectar la respuesta con un modelo de lenguaje.
6. Semana 14: integrar Chainlit y probar conversaciones completas.

Esta ruta puede cambiar, pero mantiene una progresion razonable: primero datos claros, despues pruebas, despues busqueda semantica y al final interfaz conversacional.

## 10. Conclusion

El avance de la semana 8 no convierte a Lunaria en el sistema final, pero mejora una parte necesaria: poder revisar el comportamiento de la recuperacion.

El proyecto ya puede leer su Observatorio, interpretar recomendaciones, buscar coincidencias, explicar por que las eligio y probar varios mensajes desde consola.

El siguiente paso natural es fortalecer el Observatorio y crear pruebas simples antes de saltar a embeddings, porque una busqueda semantica solo sirve si los datos base ya estan bien ordenados.
