from langchain_core.tools import tool

from .frameworks.templates import templates


@tool
def get_framework_context_tool(framework:str):
    """
    Get the context of the framework

    framework(str): The framework to get the context of

    Returns:
        str: The context of the framework
    """
    return f"The context of the framework is {templates.get(framework, 'Framework not Supported')}"
