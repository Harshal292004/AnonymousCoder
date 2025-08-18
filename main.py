from src.agent_project.application.app import Application
from src.agent_project.utilities.config import AppSettings
def main():
    print("WELCOME")
    settings=AppSettings()
    app=Application(settings)
    app.invoke()
     



if __name__ == "__main__":
    main()
