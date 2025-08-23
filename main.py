from agent_project.config.config import AppSettings
from src.agent_project.application.app import Application
import os
from src.agent_project.infrastructure.monitoring.tracing import get_langfuse_handler
def main():
    settings=AppSettings(
        GROQ_API_KEY=str(os.getenv("GROQ_API_KEY")),
        LANGFUSE_HOST=str(os.getenv("LANGFUSE_HOST")),
        LANGFUSE_SECRET_KEY=str(os.getenv("LANGFUSE_SECRET_KEY")),
        LANGFUSE_PUBLIC_KEY=str(os.getenv("LANGFUSE_PUBLIC_KEY")),
        EMBEDDINGS_MODEL_NAME="sentence-transformers/all-mpnet-base-v2",
        VECTOR_DB_FILE="user_space/trail.db",
        DEVICE="cpu"
    )
    app = Application(settings=settings)
    app.invoke()
    
if __name__ == "__main__":
    main()
