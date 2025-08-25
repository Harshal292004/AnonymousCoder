import os

from src.agent_project.application.app import Application
from src.agent_project.config.config import AppSettings


def main():
    settings=AppSettings(
        TRACING=False,
        GROQ_API_KEY=str(os.getenv("GROQ_API_KEY")),
        LANGFUSE_HOST=str(os.getenv("LANGFUSE_HOST")),
        LANGFUSE_SECRET_KEY=str(os.getenv("LANGFUSE_SECRET_KEY")),
        LANGFUSE_PUBLIC_KEY=str(os.getenv("LANGFUSE_PUBLIC_KEY")),
        EMBEDDINGS_MODEL_NAME="sentence-transformers/all-mpnet-base-v2",
        VECTOR_DB_FILE="user_space/trail.db",
        DEVICE="cpu",
        LLM_NAME="openai/gpt-oss-120b",
        LOG_FILE="user_space/logs.log",
        LOGGING=True
    )
    app = Application(settings=settings)
    app.invoke()
    
if __name__ == "__main__":
    main()
