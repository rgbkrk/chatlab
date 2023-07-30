"""Shell commands for ChatLab."""
import asyncio
import subprocess

from chatlab.decorators import expose_exception_to_llm


@expose_exception_to_llm
async def run_shell_command(command: str):
    """Run a shell command and return the output.

    Args:
    - command: str, the shell command to execute

    Returns:
    - str: the output of the shell command
    """
    process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()
    return process.returncode, stdout.decode().strip(), stderr.decode().strip()


chat_functions = [run_shell_command]
