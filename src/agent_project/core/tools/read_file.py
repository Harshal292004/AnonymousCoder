from pathlib import Path
from langchain_core.tools import tool

@tool
def read_file(path:str):
    content=""
    try:
        with open(path,mode="r") as f:
            content=f.read()
    except FileNotFoundError:
        return f"File Not found :{path}"
    except PermissionError:
        return f"Permission denied accessing: {path}"
    except Exception as e:
        return f"Error accessing {path}: {str(e)}"
   
    return content