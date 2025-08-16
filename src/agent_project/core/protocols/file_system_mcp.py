from mcp.server.fastmcp import FastMCP


mcp= FastMCP("File System")

@mcp.prompt()
def system_prompt()->str:
    """_summary_

    Returns:
        str: _description_
    """
    return  """
    """

@mcp.tool()
def remove_file():
    pass



if __name__=="__main__":
    mcp.run()