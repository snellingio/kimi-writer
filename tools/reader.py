"""
File reading tools for editing existing content.
"""

import os
from typing import Dict, List
from .project import get_active_project_folder


def read_file_impl(filename: str) -> str:
    """
    Reads content from a markdown file in the active project folder.

    Args:
        filename: The name of the file to read

    Returns:
        File content or error message
    """
    # Check if project folder is initialized
    project_folder = get_active_project_folder()
    if not project_folder:
        return "Error: No active project folder. Please specify a project folder first."

    # Ensure filename ends with .md
    if not filename.endswith('.md'):
        filename = filename + '.md'

    # Create full file path
    file_path = os.path.join(project_folder, filename)

    try:
        if not os.path.exists(file_path):
            return f"Error: File '{filename}' does not exist in the project folder."

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        word_count = len(content.split())
        return f"=== Content of '{filename}' ({word_count} words) ===\n\n{content}"

    except Exception as e:
        return f"Error reading file '{filename}': {str(e)}"


def list_files_impl() -> str:
    """
    Lists all markdown files in the active project folder.

    Returns:
        Formatted list of files with metadata or error message
    """
    # Check if project folder is initialized
    project_folder = get_active_project_folder()
    if not project_folder:
        return "Error: No active project folder. Please specify a project folder first."

    try:
        # Get all .md files in the project folder
        files = []
        for filename in sorted(os.listdir(project_folder)):
            if filename.endswith('.md') and not filename.startswith('.'):
                file_path = os.path.join(project_folder, filename)

                # Get file size and word count
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    word_count = len(content.split())
                    char_count = len(content)

                files.append({
                    'name': filename,
                    'words': word_count,
                    'chars': char_count
                })

        if not files:
            return f"No markdown files found in project folder: {os.path.basename(project_folder)}"

        # Format output
        output = f"=== Files in '{os.path.basename(project_folder)}' ({len(files)} files) ===\n\n"
        for f in files:
            output += f"- {f['name']}: {f['words']:,} words, {f['chars']:,} characters\n"

        return output

    except Exception as e:
        return f"Error listing files: {str(e)}"
