from pathlib import Path

from langchain_core.tools import tool

from .diff_files import show_diff_function


@tool
def write_code_to_file_path(path:str,content:str):
    """

    Args:
        path (str): _description_
        content (str): _description_
    """
    root=Path(path).root()
    Path(path).rename()
    
    show_diff_function()


    


