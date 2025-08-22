# CLI Agent - Anonymous Coder

A beautiful terminal-based code assistant built with Textual, featuring a modern TUI (Terminal User Interface) for an enhanced coding experience.

## Features

- 🎨 **Beautiful Terminal UI** - Modern, responsive interface built with Textual
- 🤖 **AI Code Assistant** - Powered by your choice of LLM providers
- 💾 **Memory Management** - Persistent context and project memory
- 📚 **Chat History** - Complete conversation history and session management
- ⚙️ **Settings Management** - Easy configuration of models, APIs, and preferences
- 🔍 **Code Indexing** - Intelligent codebase search and context retrieval
- ⌨️ **Keyboard Shortcuts** - Quick access to all features

## Quick Start

### 1. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
python run_app.py
```

## Usage

### Keyboard Shortcuts

- **S** - Open Settings
- **M** - Open Memories  
- **H** - Open History
- **Ctrl+C** - Quit Application

### Commands

- `/settings` - Open and manage application settings
- `/memories` - Manage and view memories
- `/history` - View chat history
- `/index` - Index codebase for search
- `/help` - Show help message
- `/clear` - Clear the chat area

### Interface

The app starts with a beautiful ASCII art welcome screen and command help. When you type your first message, the intro smoothly animates up and reveals the chat interface.

## Architecture

```
src/agent_project/
├── application/          # Main app entry point
│   └── app.py          # Textual TUI application
├── core/               # Core functionality
│   ├── graph/         # Agent workflow graph
│   ├── prompts/       # System prompts
│   ├── protocols/     # MCP protocols
│   ├── states/        # State management
│   └── tools/         # Available tools
├── infrastructure/     # External services
│   ├── databases/     # SQL and vector databases
│   ├── llm_clients/   # LLM provider clients
│   └── monitoring/    # Logging and tracing
└── utilities/         # Helper functions
    ├── config.py      # Configuration management
    ├── logger.py      # Logging utilities
    └── rich_console.py # Rich console output
```

## Configuration

The app uses a modular configuration system. Key settings can be managed through:

1. **Environment Variables** - For API keys and sensitive data
2. **Settings Screen** - Built-in TUI for configuration
3. **Configuration Files** - YAML/TOML based configs

## Development

### Adding New Tools

1. Create a new tool in `src/agent_project/core/tools/`
2. Register it in the agent graph
3. Update the command handler in the app

### Customizing the UI

The UI is built with Textual and uses CSS-like styling. Modify the `CSS` property in `AnonymousCoderApp` to customize appearance.

### Adding New Screens

1. Create a new screen class inheriting from `ModalScreen`
2. Add it to the app's action methods
3. Update bindings if needed

## Dependencies

- **Textual** - Terminal UI framework
- **Rich** - Rich text and formatting
- **LangChain** - LLM integration framework
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the existing issues
- Create a new issue with detailed description
- Include your system information and error logs