import subprocess
import os
import shutil
import tempfile
from typing import Optional, Dict, Any, List

def run_command(cmd: List[str]) -> Dict[str, Any]:
    """Executes a command using subprocess and returns output and errors."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return {
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": -2,
            "stdout": "",
            "stderr": "Error: Execution timed out"
        }

def install_dependencies(packages: Optional[List[str]], pip_path: str = "pip") -> Dict[str, Any]:
    """
    Installs pip packages using the specified pip executable.

    Args:
        packages: A list of package names to install.
        pip_path: Path to the pip executable to use.

    Returns:
        The result of the package installation command, or a no-op result if no install is needed.
    """
    if not packages:
        return {"returncode": 0, "stdout": "", "stderr": ""}  # No installation needed

    cmd = [pip_path, "install"] + packages
    return run_command(cmd)

def run_in_tempdir(code: str, packages: Optional[List[str]]) -> Dict[str, Any]:
    """
    Runs Python code in a temporary isolated virtual environment.

    Note that this does NOT mean the code is fully isolated or secure - it just means the package installations
    are isolated.

    Args:
        code: The code to run.
        packages: Optional pip packages to install in the isolated venv.

    Returns:
        Dictionary of returncode, stdout, and stderr.
    """
    temp_dir = tempfile.mkdtemp()
    venv_path = os.path.join(temp_dir, "venv")
    try:
        subprocess.run(["python3", "-m", "venv", venv_path], check=True)

        pip = os.path.join(venv_path, "bin", "pip")
        python = os.path.join(venv_path, "bin", "python")

        install_result = install_dependencies(packages, pip_path=pip)
        if install_result["returncode"] != 0:
            return {
                "returncode": install_result["returncode"],
                "stdout": install_result["stdout"],
                "stderr": f"Dependency install failed:\n{install_result['stderr']}"
            }

        return run_command([python, "-c", code])

    finally:
        shutil.rmtree(temp_dir)


def code_exec_python(code: str, packages: Optional[List[str]] = None, isolated_venv: bool = False) -> Dict[str, Any]:
    """
    Executes a Python code snippet with optional pip dependencies.

    Args:
        code: The Python code to execute as a string.
        packages: An optional list of pip package names to install before execution.
        isolated_venv: Whether to use an isolated virtual environment for this run.
            Not needed for STDIO mode; recommended but not required for SSE mode,
            to improve package isolation. Note that it will slow code execution down.

    Returns:
        A dictionary containing:
            - 'returncode': Exit status of the execution.
            - 'stdout': Captured standard output.
            - 'stderr': Captured standard error or install failure messages.
    """
    if isolated_venv:
        return run_in_tempdir(code, packages)

    install_result = install_dependencies(packages)
    if install_result["returncode"] != 0:
        return {
            "returncode": install_result["returncode"],
            "stdout": install_result["stdout"],
            "stderr": f"Dependency install failed:\n{install_result['stderr']}"
        }

    return run_command(["python3", "-c", code])