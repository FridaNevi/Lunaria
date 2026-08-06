import os

from dotenv import load_dotenv

# Segun mi hermano, mejor cargar las variables de entorno una sola vez aqui,
# en lugar de repetir load_dotenv() en cada archivo que las necesite.
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "lunaria_observatorio")

# Opcional: sin esta llave, las recomendaciones de video usan el link fijo
# del Observatorio en vez de buscar algo nuevo en YouTube.
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# Este es el modelo de embeddings que usa fastembed.
# Es multilingue y liviano, por eso corre local sin pedir GPU ni API key.
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"