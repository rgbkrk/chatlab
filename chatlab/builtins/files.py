"""Built-in functions for file operations."""
import asyncio
import os

from chatlab.decorators import expose_exception_to_llm


@expose_exception_to_llm
async def list_files(directory: str) -> list[str]:
    """List all files in the given directory.

    Args:
    - directory: str, the directory to list files from

    Returns:
    - list[str]: the list of files in the given directory

    """
    files = await asyncio.to_thread(os.listdir, directory)
    return files


@expose_exception_to_llm
async def get_file_size(file_path: str) -> int:
    """Get the size of the file in bytes asynchronously.

    Args:
    - file_path: The path to the file

    Returns:
    - The size of the file in bytes
    """
    size = await asyncio.to_thread(os.path.getsize, file_path)
    return size


@expose_exception_to_llm
async def is_file(file_path: str) -> bool:
    """Check if the given path points to a file asynchronously.

    Args:
    - file_path: The path to check

    Returns:
    - True if the path points to a file, False otherwise
    """
    is_file = await asyncio.to_thread(os.path.isfile, file_path)
    return is_file


@expose_exception_to_llm
def write_file(file_path: str, content: str, mode: str = 'w') -> None:
    """Write content to a file.

    Args:
    - file_path: The path to the file
    - content: The content to be written
    - mode: The writing mode, default is 'w' for write

    Returns:
    - None
    """
    with open(file_path, mode) as file:
        file.write(content)


@expose_exception_to_llm
def read_file(file_path: str, mode: str = 'r') -> str:
    """Read content from a file.

    Args:
    - file_path: The path to the file
    - mode: The reading mode, default is 'r' for read

    Returns:
    - str: The content of the file
    """
    with open(file_path, mode) as file:
        content = file.read()
    return content


@expose_exception_to_llm
async def is_directory(directory: str) -> bool:
    """Check if the given path points to a directory asynchronously.

    Args:
    - directory: The path to check

    Returns:
    - True if the path points to a directory, False otherwise
    """
    is_directory = await asyncio.to_thread(os.path.isdir, directory)
    return is_directory


chat_functions = [list_files, get_file_size, is_file, is_directory, write_file, read_file]
