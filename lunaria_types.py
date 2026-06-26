from enum import Enum


# Segun mi hermano, un enum es como una lista cerrada:
# aqui pongo las opciones validas para no escribir "biblioteca",
# "frecuencia" o "eclipse" de mil formas diferentes.
class LunariaMode(str, Enum):
    BIBLIOTECA = "biblioteca"
    FRECUENCIA = "frecuencia"
    CHISME = "chisme"
    ECLIPSE = "eclipse"
    CAOS = "caos"


# Estas fases funcionan como etiquetas emocionales.
# No son astronomia literal, mas bien ayudan a ordenar la vibra
# de cada recomendacion dentro del proyecto.
class MoonPhase(str, Enum):
    LUNA_NUEVA = "luna_nueva"
    CUARTO_CRECIENTE = "cuarto_creciente"
    LUNA_LLENA = "luna_llena"
    LUNA_MENGUANTE = "luna_menguante"
    ECLIPSE = "eclipse"


# Esto separa el tipo de recomendacion para que despues el sistema
# sepa si esta buscando un libro, musica, contexto cultural o apoyo emocional.
class RecommendationType(str, Enum):
    BOOK = "book"
    MUSIC = "music"
    CULTURE = "culture"
    EMOTIONAL = "emotional"
    CHAOS = "chaos"


# Aqui dejo las rutas importantes en un solo lugar.
# Segun mi hermano, esto ayuda a no andar copiando rutas por todo el codigo.
class ProjectPath(str, Enum):
    OBSERVATORIO = "observatorio/recomendaciones.md"
    SYSTEM_PROMPT = "prompts/lunaria_system.txt"
