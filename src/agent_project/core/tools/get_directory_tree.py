from langchain_core.tools import tool
import os
import pathlib

DIR_TO_AVOID = {
    # python
    '.venv','venv','__pycache__','.ruff_cache',
    # java script
    'node_modules','.next',
    # go
    'bin','vendor',
    # rust
    'target','.cargo',
    
    #java , groovy ,kotlin build tool  
    '.gradle',
    '.git'
}


def get_directory_tree_function(path: str, max_depth: int = 3, current_depth: int = 0):
    """
    Get a tree view of the directory structure.
    
    Args:
        path: The directory path to explore
        max_depth: Maximum depth to explore (default: 3)
        current_depth: Current depth level (used internally for recursion)
    
    Returns:
        A string representation of the directory tree
    """
    if current_depth > max_depth:
        return ""
    
    if not os.path.exists(path):
        return f"Path does not exist: {path}"
    
    if not os.path.isdir(path):
        return f"Not a directory: {path}"
    
    try:
        list_of_files = os.listdir(path)
        result = ""
        
        # Sort files and directories
        items = sorted(list_of_files)
        
        for i, item in enumerate(items):
            if item in DIR_TO_AVOID:
                continue
                
            item_path = os.path.join(path, item)
            is_last = (i == len(items) - 1)
            
            # Create prefix for tree structure
            prefix = "└── " if is_last else "├── "
            indent = "    " if is_last else "│   "
            
            # Add current item
            result += "  " * current_depth + prefix + item + "\n"
            
            # Recursively add subdirectories
            if os.path.isdir(item_path):
                sub_result = get_directory_tree_function(item_path, max_depth=max_depth,current_depth= current_depth + 1)
                if sub_result:
                    # Add indentation to subdirectory contents
                    sub_lines = sub_result.split('\n')
                    for line in sub_lines:
                        if line.strip():
                            result += "  " * current_depth + indent + line + "\n"
        
        return result.rstrip('\n')
        
    except PermissionError:
        return f"Permission denied accessing: {path}"
    except Exception as e:
        return f"Error accessing {path}: {str(e)}"
  
  

@tool
def get_directory_tree(path: str, max_depth: int = 3, current_depth: int = 0):
    """
    Get a tree view of the directory structure.
    
    Args:
        path: The directory path to explore
        max_depth: Maximum depth to explore (default: 3)
        current_depth: Current depth level (used internally for recursion)
    
    Returns:
        A string representation of the directory tree
    """
    return get_directory_tree_function(path,max_depth,current_depth)

if __name__ == "__main__":
    print("\n=== Testing LangChain tool ===")
    # Test the LangChain tool (using invoke method)
    result = get_directory_tree.invoke({
        "path":"/home/harshal/Desktop/Programming/cli-agent"
    })
    print(result)
