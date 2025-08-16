from langchain.tools import tool 


@tool 
def index_code_base(path:str):
    """Index code base for rag pipelines

    Args:
        path (str): Path to the root directory of the code base 
    """
    data=""
    with open(path,mode="r")  as f:
        data=f.read()
        