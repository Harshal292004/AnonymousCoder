import ast
import os
from pathlib import Path
from typing import Any, Dict, List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import tool


@tool 
def index_code_base(root_path: str = ".") -> Dict[str, Any]:
    """Index the entire codebase for RAG pipelines and code search.
    
    This tool scans through all Python files in the project, extracts code structure,
    docstrings, and creates a searchable index for better code understanding.

    Args:
        root_path (str): Path to the root directory of the codebase (default: current directory)

    Returns:
        Dict containing indexing statistics and file information
    """
    root_path = Path(root_path)
    if not root_path.exists():
        return {"error": f"Path {root_path} does not exist"}
    
    # Find all Python files
    python_files = list(root_path.rglob("*.py"))
    
    # Exclude common directories that shouldn't be indexed
    exclude_dirs = {".git", "__pycache__", ".venv", "venv", "env", ".env", "node_modules", "build", "dist"}
    
    filtered_files = []
    for file_path in python_files:
        if not any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
            filtered_files.append(file_path)
    
    indexed_files = []
    total_lines = 0
    total_functions = 0
    total_classes = 0
    
    for file_path in filtered_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the Python file to extract structure
            try:
                tree = ast.parse(content)
                file_info = _extract_file_structure(tree, content)
                file_info['file_path'] = str(file_path.relative_to(root_path))
                file_info['file_size'] = len(content)
                file_info['line_count'] = content.count('\n') + 1
                
                indexed_files.append(file_info)
                total_lines += file_info['line_count']
                total_functions += len(file_info['functions'])
                total_classes += len(file_info['classes'])
                
            except SyntaxError:
                # Handle files with syntax errors
                indexed_files.append({
                    'file_path': str(file_path.relative_to(root_path)),
                    'file_size': len(content),
                    'line_count': content.count('\n') + 1,
                    'functions': [],
                    'classes': [],
                    'imports': [],
                    'error': 'Syntax error in file'
                })
                
        except Exception as e:
            indexed_files.append({
                'file_path': str(file_path.relative_to(root_path)),
                'error': f"Could not read file: {str(e)}"
            })
    
    # Create a summary
    summary = {
        'total_files_indexed': len(indexed_files),
        'total_lines_of_code': total_lines,
        'total_functions': total_functions,
        'total_classes': total_classes,
        'root_path': str(root_path.absolute()),
        'indexed_files': indexed_files
    }
    
    return summary


def _extract_file_structure(tree: ast.AST, content: str) -> Dict[str, Any]:
    """Extract structural information from a Python AST."""
    functions = []
    classes = []
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_info = {
                'name': node.name,
                'lineno': node.lineno,
                'args': [arg.arg for arg in node.args.args],
                'docstring': ast.get_docstring(node) or ""
            }
            functions.append(func_info)
            
        elif isinstance(node, ast.ClassDef):
            class_info = {
                'name': node.name,
                'lineno': node.lineno,
                'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
                'docstring': ast.get_docstring(node) or "",
                'methods': []
            }
            
            # Extract methods from the class
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_info = {
                        'name': item.name,
                        'lineno': item.lineno,
                        'args': [arg.arg for arg in item.args.args],
                        'docstring': ast.get_docstring(item) or ""
                    }
                    class_info['methods'].append(method_info)
            
            classes.append(class_info)
            
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
                
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
    
    return {
        'functions': functions,
        'classes': classes,
        'imports': imports
    }


def search_codebase(query: str, root_path: str = ".") -> List[Dict[str, Any]]:
    """Search the codebase for specific code patterns, functions, or classes.
    
    Args:
        query (str): Search query (function name, class name, or text to search for)
        root_path (str): Path to the root directory of the codebase
        
    Returns:
        List of matching files and code snippets
    """
    # First index the codebase
    index_result = index_code_base(root_path)
    
    if 'error' in index_result:
        return [{'error': index_result['error']}]
    
    query_lower = query.lower()
    results = []
    
    for file_info in index_result['indexed_files']:
        if 'error' in file_info:
            continue
            
        file_path = file_info['file_path']
        matches = []
        
        # Search in functions
        for func in file_info['functions']:
            if (query_lower in func['name'].lower() or 
                query_lower in func['docstring'].lower()):
                matches.append({
                    'type': 'function',
                    'name': func['name'],
                    'line': func['lineno'],
                    'docstring': func['docstring']
                })
        
        # Search in classes
        for cls in file_info['classes']:
            if (query_lower in cls['name'].lower() or 
                query_lower in cls['docstring'].lower()):
                matches.append({
                    'type': 'class',
                    'name': cls['name'],
                    'line': cls['lineno'],
                    'docstring': cls['docstring']
                })
        
        if matches:
            results.append({
                'file_path': file_path,
                'matches': matches
            })
    
    return results
        
        