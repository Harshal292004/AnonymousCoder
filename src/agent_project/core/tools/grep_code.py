import re

from langchain_core.tools import tool


@tool
def grep_code(path: str, code_to_grep: str):
    """Search for code patterns in a file using regex.

    Args:
        path (str): Path to the file to search in
        code_to_grep (str): Regex pattern to search for

    Returns:
        str: Matches found with line numbers, or error message
    """
    try:
        regex = re.compile(code_to_grep, re.MULTILINE | re.IGNORECASE)
        
        matches = []
        with open(path, "r") as f:
            for idx, line in enumerate(f, start=1):
                if regex.search(line):
                    matches.append(f"{idx}|{line.rstrip()}")
                    
    except FileNotFoundError:
        return f"File Not found: {path}"
    except PermissionError:
        return f"Permission denied accessing: {path}"
    except re.error as e:
        return f"Invalid regex: {str(e)}"
    except Exception as e:
        return f"Error accessing {path}: {str(e)}"
    
    if not matches:
        return "[INFO] No matches found."
    
    return "\n".join(matches)
        


if __name__=="__main__":
    result = grep_code.invoke({
    "path": "/home/harshal/Desktop/Programming/cli-agent/src/agent_project/core/tools/grep_code.py",
    "code_to_grep": r"import\s+\w+"
    })
    print(type(result))
    print(result)