
from textual.app import  ComposeResult
from textual.widgets import (
    Footer, Input, )
from textual.containers import (
    VerticalScroll, 
    Container
)
from textual.widget import Widget
from datetime import datetime
from textual.screen import Screen
from textual.reactive import reactive


        
class IntroHeader(Widget):
    
    def render(self):
        return """

[bold white]
 █████  ███    ██  ██████  ███    ██ ██    ██ ███    ███  ██████  ██    ██ ███████ 
██   ██ ████   ██ ██    ██ ████   ██  ██  ██  ████  ████ ██    ██ ██    ██ ██      
███████ ██ ██  ██ ██    ██ ██ ██  ██   ████   ██ ████ ██ ██    ██ ██    ██ ███████ 
██   ██ ██  ██ ██ ██    ██ ██  ██ ██    ██    ██  ██  ██ ██    ██ ██    ██      ██ 
██   ██ ██   ████  ██████  ██   ████    ██    ██      ██  ██████   ██████  ███████
[/bold white]
    
[bold grey]
 ██████  ██████  ██████  ███████ ██████  
██      ██    ██ ██   ██ ██      ██   ██ 
██      ██    ██ ██   ██ █████   ██████  
██      ██    ██ ██   ██ ██      ██   ██ 
 ██████  ██████  ██████  ███████ ██   ██ 
[/bold grey]

        [bold green]Quick Commands:[/bold green]
        [bold purple]@[/bold purple] - Reference files and directories
        [bold purple]search:[/bold purple] - Search through memories
        [bold purple]ter:[/bold purple] - Execute terminal commands
        [bold purple]bye[/bold purple] or [bold purple]exit[/bold purple] - Quit application

        [bold green]Keybindings:[/bold green]
        [bold purple]s[/bold purple] - Settings
        [bold purple]m[/bold purple] - Manage Memories  
        [bold purple]h[/bold purple] - Chat History
        [bold purple]Ctrl+C[/bold purple] - Quit
        """


class ChatMessage(Widget):
    """Widget for displaying chat messages"""
    
    def __init__(self, role: str, content: str,timestamp:str):
        super().__init__()
        self.role = role
        self.content = content
        self.timestamp = timestamp  
    def render(self) -> str:
        role_color = "yellow" if self.role == "user" else "green"
        return f"[{role_color}]{self.role.upper()}[/{role_color}] [{self.timestamp}]\n{self.content}\n"

class MainScreen(Screen):
    """Main chat interface screen"""
    
    messages_shown = reactive(False)
    
    def __init__(self):
        super().__init__()
        self.chat_messages = []
    
    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            IntroHeader(),
            Container(id="chat_container"),
            id="main_scroll"
        )
        yield Input(placeholder="What's on your mind today...", id="user_input")
        yield Footer()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input submission"""
        if event.value.strip():
            self.add_message("user", event.value)
            
            # Process the input
            if event.value.lower() in {"bye", "exit"}:
                self.app.exit()
            elif event.value.startswith("@"):
                self.add_message("assistant", "File reference feature coming soon!")
            elif event.value.startswith("search:"):
                self.add_message("assistant", "Memory search feature coming soon!")
            elif event.value.startswith("ter:"):
                self.add_message("assistant", "Terminal command execution coming soon!")
            else:
                # Simulate AI response
                self.add_message("assistant", f"I received your message: '{event.value}'. This is where the AI response would appear.")
            
            # Clear input
            event.input.value = ""
    
    def add_message(self, role: str, content: str,timestamp:str=datetime.now().strftime("%H:%M:%S")) -> None:
        """Add a new message to the chat"""
        message = ChatMessage(role, content,timestamp=timestamp)
        self.chat_messages.append(message)
        
        chat_container = self.query_one("#chat_container", Container)
        chat_container.mount(message)
        
        # If this is the first message, hide the intro and scroll
        if not self.messages_shown:
            self.messages_shown = True
            main_scroll = self.query_one("#main_scroll", VerticalScroll)
            main_scroll.scroll_end(animate=True)