import difflib
from pathlib import Path

from langchain_core.tools import tool


def load_file(path: str):
    try:
        lines = Path(path).read_text().splitlines()
        return lines  # Don't strip whitespace to preserve formatting
    except FileNotFoundError:
        return [f"[ERROR] File not found: {path}"]
    except PermissionError:
        return [f"[ERROR] Permission denied: {path}"]
    except Exception as e:
        return [f"[ERROR] Could not read {path}: {str(e)}"]

def show_diff_function(file_one_path: str, file_two_path: str, context: int = 3, ignore_whitespace: bool = True)->str:
    """
    Compare two files and show the differences between them in git-like format.
    
    Args:
        file_one_path: Path to the first file (old version)
        file_two_path: Path to the second file (new version)
        context: Number of context lines to show around each difference (default: 3)
        ignore_whitespace: Whether to ignore whitespace differences (default: True)
    
    Returns:
        A git-like diff showing the differences between the two files, or an error message if files cannot be read.
    """
    try:
        if ignore_whitespace:
            old_lines = load_file(file_one_path)
            new_lines = load_file(file_two_path)
        else:
            try:
                old_lines = Path(file_one_path).read_text().splitlines()
            except Exception as e:
                return f"[ERROR] Failed to read {file_one_path}: {e}"
            try:
                new_lines = Path(file_two_path).read_text().splitlines()
            except Exception as e:
                return f"[ERROR] Failed to read {file_two_path}: {e}"

        # Generate git-like diff
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_one_path}",
            tofile=f"b/{file_two_path}",
            n=context,
            lineterm=""
        )

        result = list(diff)
        
        if not result:
            return "[INFO] No differences found."
        
        # Add git-style header if there are differences
        header = [
            f"diff --git a/{file_one_path} b/{file_two_path}",
            f"index 0000000..0000000 100644",
            f"--- a/{file_one_path}",
            f"+++ b/{file_two_path}"
        ]
        
        # Combine header with diff result
        full_diff = header + result
        
        return "\n".join(full_diff)
        
    except Exception as e:
        return f"[ERROR] Unexpected failure: {e}"

@tool
def show_diff(file_one_path: str, file_two_path: str, context: int = 3, ignore_whitespace: bool = True):
    """
    Compare two files and show the differences between them in git-like format.
    
    Args:
        file_one_path: Path to the first file (old version)
        file_two_path: Path to the second file (new version)
        context: Number of context lines to show around each difference (default: 3)
        ignore_whitespace: Whether to ignore whitespace differences (default: True)
    
    Returns:
        A git-like diff showing the differences between the two files, or an error message if files cannot be read.
    """
    return show_diff_function(file_one_path, file_two_path, context, ignore_whitespace)

if __name__ == "__main__":
    print("\n=== Testing LangChain tool ===")
    # Test the LangChain tool (using invoke method)
    result = show_diff.invoke({
        "file_one_path": "src/agent_project/core/tools/diff_files.py",
        "file_two_path": "src/agent_project/core/tools/read_file.py"
    })
    print(result)
