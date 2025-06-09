import shutil
import subprocess
import sys
from pathlib import Path


def build_installer():
    """Compila o instalador em um executável Windows"""

    # Diretórios
    script_dir = Path(__file__).parent
    installer_script = script_dir / "installer.py"
    build_dir = script_dir / "build"
    dist_dir = script_dir / "dist"

    # Limpar diretórios anteriores
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    print("Compilando instalador...")

    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name",
        "RepensenAssistente-Installer",
        "--icon",
        str(script_dir / "icon.ico") if (script_dir / "icon.ico").exists() else None,
        "--add-data",
        f"{script_dir / 'icon.ico'};." if (script_dir / "icon.ico").exists() else "",
        "--hidden-import",
        "tkinter",
        "--hidden-import",
        "tkinter.ttk",
        "--hidden-import",
        "tkinter.messagebox",
        "--hidden-import",
        "tkinter.scrolledtext",
        "--hidden-import",
        "requests",
        "--hidden-import",
        "zipfile",
        "--hidden-import",
        "json",
        "--hidden-import",
        "subprocess",
        "--hidden-import",
        "threading",
        "--hidden-import",
        "webbrowser",
        "--hidden-import",
        "datetime",
        "--hidden-import",
        "pathlib",
        "--hidden-import",
        "tempfile",
        "--hidden-import",
        "shutil",
        str(installer_script),
    ]

    # Remover argumentos vazios
    cmd = [arg for arg in cmd if arg]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Compilação concluída com sucesso!")
        print(f"Executável criado em: {dist_dir / 'RepensenAssistente-Installer.exe'}")

        # Criar arquivo de versão
        version_file = dist_dir / "version.txt"
        with open(version_file, "w") as f:
            f.write("1.0.0\n")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Erro na compilação: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False


def install_dependencies():
    """Instala dependências necessárias"""
    dependencies = ["pyinstaller", "requests", "pathlib"]

    print("Instalando dependências...")
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            print(f"✓ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"✗ Erro ao instalar {dep}")
            return False

    return True


if __name__ == "__main__":
    print("=== Build do Instalador Repense Assistente ===")

    if not install_dependencies():
        print("Erro ao instalar dependências")
        sys.exit(1)

    if build_installer():
        print("\n✓ Build concluído com sucesso!")
        print("O instalador está pronto para distribuição.")
    else:
        print("\n✗ Erro no build")
        sys.exit(1)
