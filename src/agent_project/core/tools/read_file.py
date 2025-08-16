from pathlib import Path
from langchain.tools import tool

@tool
def read_file(path:str):
    content=""
    
    with open(path,mode="r") as f:
        content=f.read()
    
    return content