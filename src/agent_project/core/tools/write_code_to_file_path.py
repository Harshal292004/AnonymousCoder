from langchain_core.tools import tool
from tools.diff_files import show_diff_function
import os
from pathlib import  Path
from uuid import uuid4
@tool
def write_code_to_file_path(path:str,content:str):
    
    root=Path(path).root()
    Path(path).rename()
    
    show_diff_function()


    
    pass


