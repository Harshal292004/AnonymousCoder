from src.agent_project.utilities.config import AppSettings
from src.agent_project.application.app import Application
import os

def main():
    # settings=AppSettings()
    # app=Application(settings)
    # app.invoke()
    settings=AppSettings(
        LANGFUSE_PUBLIC_KEY=str(os.getenv("LANGFUSE_PUBLIC_KEY")),
        EMBEDDINGS_MODEL_NAME="sentence-transformers/all-mpnet-base-v2",
        VECTOR_DB_FILE="user_space/trail.db",
        DEVICE="cpu"
    )
    app = Application(settings=settings)
    app.invoke()
if __name__ == "__main__":
    main()
