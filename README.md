## CLI Agent

A command-line AI agent that executes tasks directly from your terminal. It combines LangChain, LangGraph, and a small set of file-system tools with optional tracing and persistence, so you can iterate on code and content from a single interactive prompt.

### Project status
- This project is under active development. Several nodes, protocols, and tools are stubs and will evolve.
- The Dockerfile is a placeholder and not ready for production.

## Features
- **Interactive CLI chat loop**: Run `python main.py` and converse with the agent; type `bye` or `exit` to quit.
- **LangGraph orchestration**: Pluggable node graph (`code_graph`) for routing requests.
- **Persistence**: SQLite-backed thread and message store via `DataBaseManager`.
- **Vector search (optional)**: SQLite-Vec vector store wrapper for embedding and search.
- **LLM providers**: OpenAI, Google Generative AI, Groq, and Ollama via LangChain wrappers.
- **Tools for codebases**:
  - `get_directory_tree`: Inspect directory structure with ignore lists and depth limits.
  - `read_file`: Safely read files with helpful errors.
  - `show_diff`: Unified diff between two files in git-like format.
  - `create_file` / `delete_file`: Create or remove files with safety checks.
- **Observability (optional)**: Langfuse callback handler for tracing.

## Architecture at a glance
- **Entry point**: `main.py` initializes `Application` and starts the chat loop.
- **Application**: `src/agent_project/application/app.py`
  - Creates a thread (UUID) and tracks all messages.
  - Dispatches messages to the LangGraph `code_graph`.
  - Handles exit and reserved prefixes (`@`, `search:`, `ter:`) which are placeholders today.
- **Graph**: `src/agent_project/core/graph/graph.py`
  - Registers nodes like `memory_node`, `understand_query_node`, `general_query_node`, `index_code_base_node`, `scaffold_project_node` (currently stubs in `nodes.py`).
- **Persistence**: `src/agent_project/infrastructure/databases/sql_database.py`
  - Stores threads and messages; returns LangChain-compatible message objects.
- **Vector store**: `src/agent_project/infrastructure/databases/vector_database.py`
  - Thin wrapper around `SQLiteVec` and `OpenAIEmbeddings` for similarity search.
- **LLMs**: `src/agent_project/infrastructure/llm_clients/llms.py`
  - Unified config and providers: OpenAI, Google, Groq, Ollama.
- **Tools**: `src/agent_project/core/tools/*`
  - Implement discrete file and codebase utilities as LangChain tools.
- **System prompt**: `src/agent_project/core/prompts/system_prompt.py` (placeholder).
- **MCP protocol**: `src/agent_project/core/protocols/file_system_mcp.py` (experimental placeholder).

## Requirements
- **Python**: 3.12+
- **OS**: Linux, macOS, or Windows (some tools are POSIX-oriented; Windows support is partial).
- **Optional local services**: Ollama (for local models).

## Installation
You can install dependencies via `pip` using the provided `requirements.txt`, or via the `pyproject.toml` project metadata.

### Using pip and a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### Editable install (optional)
```bash
pip install -e .
```

## Configuration
Create a `.env` file in the project root (or export env vars in your shell) for the providers you plan to use.

- **OpenAI**
  - `OPENAI_API_KEY`
- **Google Generative AI**
  - `GOOGLE_API_KEY`
- **Groq**
  - `GROQ_API_KEY`
- **Ollama** (optional local models)
  - `OLLAMA_BASE_URL` (default `http://localhost:11434`)
- **Langfuse** (optional tracing)
  - `LANGFUSE_PUBLIC_KEY` (used by the provided callback helper)

Note: The vector store defaults to `OpenAIEmbeddings`, which requires a valid `OPENAI_API_KEY` if you use vector features.

## Quickstart
```bash
python main.py
```
You will see:
```
WELCOME
Enter your query please : 
```
- Type your request and press Enter.
- Type `bye` or `exit` to quit.

Reserved prefixes (placeholders, not yet implemented):
- `@path/to/file` or similar: intended for path-aware interactions.
- `search: ...`: intended for memory or vector retrieval.
- `ter: ...`: intended for raw terminal command execution.

## Examples
- **Inspect a directory tree**
  - Ask: "Show me the tree for this repo up to depth 2"
  - The agent may call `get_directory_tree` to produce a structured view.
- **Compare two files**
  - Ask: "What changed between file A and file B?"
  - The agent may call `show_diff` and return a unified diff.
- **Read a file**
  - Ask: "Open `src/agent_project/core/tools/read_file.py`"
  - The agent may call `read_file` and stream back contents safely.

## Development
- **Code style**: Prefer clear, descriptive names and early returns; keep functions small.
- **Graph nodes**: See `src/agent_project/core/graph/nodes.py` for stubs to implement.
- **New tools**: Add in `src/agent_project/core/tools/` using LangChain's `@tool` decorator.
- **Local models**: If using Ollama, ensure the model is pulled and the service is running.

### Useful scripts
Run the CLI:
```bash
python main.py
```

### Docker
The current `Dockerfile` is not complete. Containerization instructions will be provided in a future update.

## Troubleshooting
- "No module named ...": Ensure your virtual environment is activated and dependencies are installed.
- Vector search not working: Ensure `OPENAI_API_KEY` is set (default embedding model is OpenAI).
- Access errors reading files: The tools surface permission and not-found errors; verify paths and permissions.

## Roadmap
- Fill in graph nodes for query understanding, memory, scaffolding, and code indexing.
- Implement terminal execution and path-addressable commands.
- Expand tracing and add Langfuse project configuration.
- Complete Docker support and CI.
- Add tests and examples.

## License
No license file is currently provided. Add a suitable license before distribution.