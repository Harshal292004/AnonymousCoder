from pydantic import Field
from langchain_core.tools import tool
from pathlib import Path
import logging


@tool
def create_file(path: str, content:str,overwrite: bool = False) -> str:
    """
    Create a new file at the specified path with optional content.
    
    Args:
        path: The file path where the file should be created
        content: The content to write to the file (default: empty string)
        overwrite: Whether to overwrite existing files (default: False)
    
    Returns:
        A success message indicating the file was created
        
    Raises:
        FileExistsError: If the file already exists and overwrite is False
        PermissionError: If there are permission issues
        OSError: For other file system errors
    """
    try:
        file_path = Path(path)
        
        # Check if file exists and handle overwrite logic
        if file_path.exists() and not overwrite:
            raise FileExistsError(f"File '{path}' already exists. Use overwrite=True to overwrite.")
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully created file {path} and written {len(content)} characters to it"
        
    except FileExistsError as e:
        logging.error(f"File creation failed: {e}")
        raise
    except PermissionError as e:
        logging.error(f"Permission denied creating file '{path}': {e}")
        raise
    except OSError as e:
        logging.error(f"Error creating file '{path}': {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error creating file '{path}': {e}")
        raise


@tool
def delete_file(path: str, force: bool = False) -> str:
    """
    Delete a file at the specified path.
    
    Args:
        path: The file path to delete
        force: Whether to force deletion without confirmation (default: False)
    
    Returns:
        A success message indicating the file was deleted
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If there are permission issues
        OSError: For other file system errors
    """
    try:
        file_path = Path(path)
        
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File '{path}' does not exist.")
        
        # Check if it's actually a file (not a directory)
        if not file_path.is_file():
            raise OSError(f"'{path}' is not a file (it might be a directory).")
        
        # Delete the file
        file_path.unlink()
        
        return f"Successfully deleted file '{path}'."
        
    except FileNotFoundError as e:
        logging.error(f"File deletion failed: {e}")
        raise
    except PermissionError as e:
        logging.error(f"Permission denied deleting file '{path}': {e}")
        raise
    except OSError as e:
        logging.error(f"Error deleting file '{path}': {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error deleting file '{path}': {e}")
        raise