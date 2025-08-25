
from textual.app import App

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
    