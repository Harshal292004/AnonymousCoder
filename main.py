import os
from json import load

from dotenv import load_dotenv

from src.agent_project.application.app import Application
from src.agent_project.config.config import AppSettings


def load_json(settings_path:str="user_space/settings.json"):
    with open(settings_path,"r")  as f:
        user_settings=load(f)
    return user_settings
def main():
    load_dotenv()
    # Get environment variables with defaults
    # This all will be set in the settings page of terminal
    # Model to use , its api key , Whether to use observatory or not
    
    # User provided API keys
    # llm_api_key
    api_key = os.getenv("API_KEY")
    
    # For developement only
    langfuse_host = os.getenv("LANGFUSE_HOST")
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    
    
    
    # System default shipped with the product
    # halt for now untill indexing of cde base is needed 
    # qdrant_host = os.getenv("QDRANT_HOST")
    # qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    
    # load user settings
    user_settings=load_json(settings_path="user_space/settings.json")    
    settings = AppSettings(
        TRACING=user_settings.get("TRACING"),
        API_KEY=api_key,
        LANGFUSE_HOST=langfuse_host,
        LANGFUSE_SECRET_KEY=langfuse_secret_key,
        LANGFUSE_PUBLIC_KEY=langfuse_public_key,
        EMBEDDINGS_MODEL_NAME="sentence-transformers/all-mpnet-base-v2",
        QDRANT_COLLECTION="app_documents",
        LLM_NAME="openai/gpt-oss-120b",
        LOG_FILE="user_space/logs.log",
        LOGGING=True
    )
    
    # Create the application instance directly
    app = Application(
        settings=settings,
        database=None,  # Will be set in model_post_init
        tracer=None,    # Will be set in model_post_init
        thread_id="",   # Will be set in model_post_init
        graph=None      # Will be set in model_post_init
    )
    
    app.invoke()
    
if __name__ == "__main__":
    main()
