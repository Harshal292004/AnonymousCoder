# from pydantic import BaseModel
# from uuid import uuid4
# from ..utilities.config import AppSettings
# from core.graph.graph import create_graph
# from langchain_core.messages import HumanMessage, SystemMessage, AIMessage,ToolMessage
# from core.states.AnonymousState import AnonymousState
# from infrastructure.databases.sql_database import DataBaseManager
# from infrastructure.llm_clients.llms import ModelProvider,LLMConfig,GroqLLM
## this is the application where everything starts
## lets work it out till only memory_node with the cli
## add a wrapper aorund everynode with
## add tabs feature
# class Application(BaseModel):

#     def __init__(self,settings:AppSettings):
#         self.settings=settings
#         self.database=DataBaseManager(db_path="temp.db")
#         pass

#     def invoke(self):
#         self._chat()
#         pass

#     def _chat(self):
#         #  intiate the data base with the current data base
#         thread_id=str(uuid4())
#         self.database.create_thread(thread_id=thread_id)
#         while True:
#             query=input("Enter your query please : ")
#             message_id=str(uuid4())
#             self.database.add_human_message(thread_id=thread_id,message_id=message_id,content=query)
#             if query.lower() in {"bye","exit"}:
#                 print("Exiting the world...:(")
#                 exit(1)
#             elif query.startswith("@"):
#                 # find path
#                 # matbal mujhe karna nahi chaiye na

#                 pass
#             elif query.startswith("search:"):
#                 # look in memory
#                 pass
#             elif query.startswith("ter:"):
#                 #TODO: run normal terminal commands

#                 pass
#             else:
#                 #run the graph with prompt history
#                 # append messages in the prompt with System Prompt
#                 output=code_graph.invoke(AnonymousState(messages=[HumanMessage(query)],error_count=0))
#                 message_id=str(uuid4())
#                 self.database.add_ai_message(thread_id=thread_id,message_id=message_id,content=output["messages"])

#         #TODO: after the execution get summary of recente chats in the thread and insert them as a context into the data base so we can refrecne the chats
#         #TODO: future feature
from textual.app import App, ComposeResult
from textual.widgets import (
    Footer, Input, Static, Button, Label, TextArea, 
    DataTable, ListView, ListItem, Select, Switch, 
    Collapsible, OptionList, Placeholder, Tabs, TabPane
)
from textual.widget import Widget
from textual.containers import (
    VerticalScroll, VerticalGroup, HorizontalGroup, 
    Container, Horizontal, Vertical, Grid
)
from textual.screen import Screen, ModalScreen
from textual.reactive import reactive
from textual.message import Message
from textual.validation import Number
from textual import events
from datetime import datetime
import uuid
from .main_screen import MainScreen

class AnonymousCoderApp(App):
    """A Textual app for coding through CLI"""

    BINDINGS = [
        # ("s", "push_screen('settings')", "Settings"),
        # ("m", "push_screen('memories')", "Memories"),
        # ("h", "push_screen('history')", "History"),
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+d", "toggle_dark", "Toggle Dark Mode"),
    ]
    
    CSS_PATH="app.tcss"
    # SCREENS = {
    #     "settings": SettingsScreen,
    #     "memories": MemoryManagementScreen,
    #     "history": ChatHistoryScreen,
    # }

    def on_mount(self) -> None:
        """Called when app starts."""
        self.install_screen(MainScreen(), name="main")
        self.push_screen("main")

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = AnonymousCoderApp()
    app.run()
    