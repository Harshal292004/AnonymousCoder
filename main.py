# from src.agent_project.application.app import Application
# from src.agent_project.utilities.config import AppSettings

from src.agent_project.application.app import AnonymousCoderApp

def main():
    # settings=AppSettings()
    # app=Application(settings)
    # app.invoke()
    app = AnonymousCoderApp()
    app.run()
     



if __name__ == "__main__":
    main()
