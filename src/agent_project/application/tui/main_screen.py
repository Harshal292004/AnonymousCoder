from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, Input


class IntroHeader(Widget):

    def render(self):
        return """

[bold #bae51a]
 █████  ███    ██  ██████  ███    ██ ██    ██ ███    ███  ██████  ██    ██ ███████ 
██   ██ ████   ██ ██    ██ ████   ██  ██  ██  ████  ████ ██    ██ ██    ██ ██      
███████ ██ ██  ██ ██    ██ ██ ██  ██   ████   ██ ████ ██ ██    ██ ██    ██ ███████ 
██   ██ ██  ██ ██ ██    ██ ██  ██ ██    ██    ██  ██  ██ ██    ██ ██    ██      ██ 
██   ██ ██   ████  ██████  ██   ████    ██    ██      ██  ██████   ██████  ███████
[/bold #bae51a]
    
[bold white]
 ██████  ██████  ██████  ███████ ██████  
██      ██    ██ ██   ██ ██      ██   ██ 
██      ██    ██ ██   ██ █████   ██████  
██      ██    ██ ██   ██ ██      ██   ██ 
 ██████  ██████  ██████  ███████ ██   ██ 
[/bold white]

        [bold #bae51a]Quick Commands:[/bold #bae51a]
        [bold #e3b81c]@[/bold #e3b81c] - Reference files and directories
        [bold #e3b81c]search:[/bold #e3b81c] - Search through memories
        [bold #e3b81c]ter:[/bold #e3b81c] - Execute terminal commands
        [bold #e3b81c]bye[/bold #e3b81c] or [bold #e3b81c]exit[/bold #e3b81c] - Quit application

        [bold #bae51a]Keybindings:[/bold #bae51a]
        [bold #e3b81c]s[/bold #e3b81c] - Settings
        [bold #e3b81c]m[/bold #e3b81c] - Manage Memories  
        [bold #e3b81c]h[/bold #e3b81c] - Chat History
        [bold #e3b81c]Ctrl+C[/bold #e3b81c] - Quit
        """


class ChatMessage(Widget):
    """Widget for displaying chat messages"""

    def __init__(self, role: str, content: str, timestamp: str):
        super().__init__()
        self.role = role
        self.content = content
        self.timestamp = timestamp

    def render(self) -> str:
        role_color = "yellow" if self.role == "user" else "#bae51a"
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
        with Container(id="input_container"):
            yield Input(
                placeholder="What's on your mind today...", 
                id="user_input"
            )
        yield Footer()
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input submission"""
        if event.value.strip():
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
                self.add_message("user", event.value)
                
            # Clear input
            event.input.value = ""

    def add_message(
        self,
        role: str,
        content: str,
        timestamp: str = datetime.now().strftime("%H:%M:%S"),
    ) -> None:
        """Add a new message to the chat"""
        message = ChatMessage(role, content, timestamp=timestamp)
        self.chat_messages.append(message)

        chat_container = self.query_one("#chat_container", Container)
        chat_container.mount(message)

        # If this is the first message, hide the intro and scroll
        if not self.messages_shown:
            self.messages_shown = True
            main_scroll = self.query_one("#main_scroll", VerticalScroll)
            main_scroll.scroll_end(animate=True)
