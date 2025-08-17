from langchain_core.tools import tool 
import os 

@tool
def get_current_directory()->str:
    """Gives current working directory as a string
    

    Returns:
        str: _description_
    """
    
    return os.getcwd()