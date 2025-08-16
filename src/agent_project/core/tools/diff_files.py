import difflib
from pathlib import Path
from langchain.tools import tool

@tool
def load_file(path):
    # Normalize whitespace (collapse spaces/tabs)
    lines = Path(path).read_text().splitlines()
    return [line.strip() for line in lines]

def show_diff(file_old, file_new, context=3, ignore_whitespace=True):
    old_lines = load_file(file_old) if ignore_whitespace else Path(file_old).read_text().splitlines()
    new_lines = load_file(file_new) if ignore_whitespace else Path(file_new).read_text().splitlines()

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=file_old,
        tofile=file_new,
        n=context,        # number of context lines (like context: 3)
        lineterm=""
    )

    print("\n".join(diff))


# Example usage
show_diff("file_before.py", "file_after.py", context=3, ignore_whitespace=True)
