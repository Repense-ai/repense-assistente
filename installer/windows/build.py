import os
import shutil
import subprocess
import sys
from pathlib import Path

# --- Configuration ---
SCRIPT_DIR = Path(__file__).resolve().parent
VENV_DIR = SCRIPT_DIR / ".venv"
VENV_PYTHON = (
    VENV_DIR / "Scripts" / "python.exe"
    if sys.platform == "win32"
    else VENV_DIR / "bin" / "python"
)
REQUIREMENTS_FILE = SCRIPT_DIR / "requirements.txt"
SPEC_FILE = SCRIPT_DIR / "installer.spec"
BUILD_DIR = SCRIPT_DIR / "build"
DIST_DIR = SCRIPT_DIR / "dist"


def log(message, level="INFO"):
    """Logs a message to the console."""
    print(f"[{level}] {message}")


def run_command(command, cwd=None):
    """Executes a command and streams its output."""
    log(f"Running command: {' '.join(str(c) for c in command)}")
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
        )
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())
        return process.poll()
    except FileNotFoundError:
        log(f"Error: Command not found: {command[0]}", "ERROR")
        return 1
    except Exception as e:
        log(f"An unexpected error occurred: {e}", "ERROR")
        return 1


def create_virtual_environment():
    """Creates a virtual environment if it doesn't exist."""
    if VENV_DIR.exists():
        log("Virtual environment already exists.")
        return True

    log("Creating virtual environment...")
    return_code = run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
    if return_code != 0:
        log("Failed to create virtual environment.", "ERROR")
        return False
    return True


def install_dependencies():
    """Installs dependencies from requirements.txt into the virtual environment."""
    if not REQUIREMENTS_FILE.exists():
        log(f"'{REQUIREMENTS_FILE}' not found.", "ERROR")
        return False

    log("Installing dependencies...")
    return_code = run_command(
        [str(VENV_PYTHON), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)]
    )
    if return_code != 0:
        log("Failed to install dependencies.", "ERROR")
        return False
    log("Dependencies installed successfully.")
    return True


def clean_build_folders():
    """Removes previous build artifacts."""
    log("Cleaning up previous build artifacts...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        log(f"Removed '{BUILD_DIR}'")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        log(f"Removed '{DIST_DIR}'")


def run_pyinstaller():
    """Runs PyInstaller to build the executable."""
    if not SPEC_FILE.exists():
        log(f"PyInstaller spec file not found: '{SPEC_FILE}'", "ERROR")
        return False

    log("Running PyInstaller...")
    command = [
        str(VENV_PYTHON),
        "-m",
        "PyInstaller",
        str(SPEC_FILE),
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--clean",
    ]
    return_code = run_command(command, cwd=SCRIPT_DIR)
    if return_code != 0:
        log("PyInstaller build failed.", "ERROR")
        return False
    log("PyInstaller build completed successfully.")
    return True


def main():
    """Main build process orchestrator."""
    print("--- Repense Assistente Installer Build ---")

    if not create_virtual_environment():
        sys.exit(1)

    if not install_dependencies():
        sys.exit(1)

    clean_build_folders()

    if not run_pyinstaller():
        sys.exit(1)

    installer_path = DIST_DIR / "repense-assistente.exe"
    if installer_path.exists():
        log(f"\nBuild successful! Installer created at:")
        log(str(installer_path), "SUCCESS")
    else:
        log("\nBuild failed. Installer executable not found.", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main() 