import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import tkinter as tk
import webbrowser
import zipfile
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk
from typing import Any

import requests


class RepensenAssistenteInstaller:
    def __init__(self):
        self.app_name = "Repense Assistente"
        self.version = "1.0.0"
        self.github_repo = (
            "seu-usuario/repense-assistente"  # Substitua pelo seu repositório
        )
        self.install_dir = Path.home() / "RepensenAssistente"
        self.config_file = self.install_dir / "config.json"
        self.docker_compose_file = self.install_dir / "docker-compose.yml"

        # URLs para download
        self.github_api_url = (
            f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        )
        self.github_download_url = (
            f"https://github.com/{self.github_repo}/archive/refs/heads/main.zip"
        )

        # Interface gráfica
        self.root = None
        self.progress_var = None
        self.status_var = None
        self.log_text = None

        # Estado da aplicação
        self.is_running = False
        self.containers_status = {}

    def setup_gui(self):
        """Configura a interface gráfica do instalador"""
        self.root = tk.Tk()
        self.root.title(f"{self.app_name} - Instalador")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Variáveis de controle
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Pronto para instalar")

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Título
        title_label = ttk.Label(
            main_frame, text=self.app_name, font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Status
        status_label = ttk.Label(main_frame, text="Status:")
        status_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        status_display = ttk.Label(main_frame, textvariable=self.status_var)
        status_display.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Barra de progresso
        progress_label = ttk.Label(main_frame, text="Progresso:")
        progress_label.grid(row=2, column=0, sticky=tk.W, pady=5)

        self.progress_bar = ttk.Progressbar(
            main_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.grid(
            row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(0, 10)
        )

        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)

        self.install_btn = ttk.Button(
            button_frame, text="Instalar/Atualizar", command=self.install_or_update
        )
        self.install_btn.pack(side=tk.LEFT, padx=5)

        self.start_btn = ttk.Button(
            button_frame,
            text="Iniciar Serviços",
            command=self.start_services,
            state=tk.DISABLED,
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            button_frame,
            text="Parar Serviços",
            command=self.stop_services,
            state=tk.DISABLED,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.open_btn = ttk.Button(
            button_frame,
            text="Abrir Interface",
            command=self.open_interface,
            state=tk.DISABLED,
        )
        self.open_btn.pack(side=tk.LEFT, padx=5)

        self.uninstall_btn = ttk.Button(
            button_frame, text="Desinstalar", command=self.uninstall
        )
        self.uninstall_btn.pack(side=tk.LEFT, padx=5)

        # Log
        log_label = ttk.Label(main_frame, text="Log:")
        log_label.grid(row=4, column=0, sticky=(tk.W, tk.N), pady=(10, 0))

        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.log_text.grid(
            row=4, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0)
        )

        # Verificar status inicial
        self.check_initial_status()

    def log(self, message: str):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        if self.log_text:
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
            self.root.update_idletasks()

        print(log_message.strip())

    def update_status(self, status: str):
        """Atualiza o status na interface"""
        if self.status_var:
            self.status_var.set(status)
            self.root.update_idletasks()

    def update_progress(self, value: float):
        """Atualiza a barra de progresso"""
        if self.progress_var:
            self.progress_var.set(value)
            self.root.update_idletasks()

    def check_docker_installed(self) -> bool:
        """Verifica se o Docker está instalado"""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.log(f"Docker encontrado: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass

        self.log("Docker não encontrado")
        return False

    def check_docker_compose_installed(self) -> bool:
        """Verifica se o Docker Compose está instalado"""
        try:
            result = subprocess.run(
                ["docker", "compose", "version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.log(f"Docker Compose encontrado: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass

        # Tentar versão standalone
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.log(
                    f"Docker Compose (standalone) encontrado: {result.stdout.strip()}"
                )
                return True
        except FileNotFoundError:
            pass

        self.log("Docker Compose não encontrado")
        return False

    def install_docker_desktop(self):
        """Guia o usuário para instalar o Docker Desktop"""
        message = (
            "Docker não foi encontrado no sistema.\n\n"
            "Para usar o Repense Assistente, você precisa instalar o Docker Desktop.\n\n"
            "Clique em 'Sim' para abrir a página de download do Docker Desktop.\n"
            "Após a instalação, reinicie este instalador."
        )

        if messagebox.askyesno("Docker não encontrado", message):
            webbrowser.open("https://www.docker.com/products/docker-desktop/")

        return False

    def check_for_updates(self) -> dict[str, Any] | None:
        """Verifica se há atualizações disponíveis"""
        try:
            self.log("Verificando atualizações...")
            response = requests.get(self.github_api_url, timeout=10)

            if response.status_code == 200:
                release_info = response.json()
                latest_version = release_info.get("tag_name", "unknown")

                # Verificar se há uma versão mais nova
                if self.is_newer_version(latest_version, self.version):
                    self.log(f"Nova versão disponível: {latest_version}")
                    return release_info
                else:
                    self.log("Você já tem a versão mais recente")
                    return None
            else:
                self.log(f"Erro ao verificar atualizações: {response.status_code}")
                return None

        except Exception as e:
            self.log(f"Erro ao verificar atualizações: {e!s}")
            return None

    def is_newer_version(self, latest: str, current: str) -> bool:
        """Compara versões para determinar se há uma mais nova"""
        try:
            # Remove 'v' se presente
            latest = latest.lstrip("v")
            current = current.lstrip("v")

            latest_parts = [int(x) for x in latest.split(".")]
            current_parts = [int(x) for x in current.split(".")]

            # Normalizar tamanhos
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))

            return latest_parts > current_parts
        except:
            return False

    def download_and_extract(self) -> bool:
        """Baixa e extrai os arquivos do projeto"""
        try:
            self.log("Baixando arquivos do projeto...")
            self.update_status("Baixando...")

            # Criar diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = Path(temp_dir) / "project.zip"

                # Baixar arquivo
                response = requests.get(self.github_download_url, stream=True)
                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(zip_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = (
                                    downloaded / total_size
                                ) * 50  # 50% para download
                                self.update_progress(progress)

                self.log("Download concluído, extraindo arquivos...")
                self.update_status("Extraindo arquivos...")

                # Extrair arquivo
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Encontrar diretório extraído
                extracted_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir()]
                if not extracted_dirs:
                    raise Exception("Nenhum diretório encontrado no arquivo extraído")

                source_dir = extracted_dirs[0]

                # Criar diretório de instalação
                self.install_dir.mkdir(parents=True, exist_ok=True)

                # Copiar arquivos
                self.log("Copiando arquivos para diretório de instalação...")
                for item in source_dir.iterdir():
                    dest = self.install_dir / item.name
                    if item.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)

                self.update_progress(75)

            self.log("Arquivos instalados com sucesso")
            return True

        except Exception as e:
            self.log(f"Erro ao baixar/extrair arquivos: {e!s}")
            return False

    def create_env_file(self):
        """Cria arquivo .env com configurações padrão"""
        env_file = self.install_dir / ".env"

        if not env_file.exists():
            self.log("Criando arquivo de configuração...")

            env_content = """# Configurações do Repense Assistente
OPENAI_API_KEY=your_openai_api_key_here
REDIS_URL=redis://redis:6379

# Configurações do WAHA
WAHA_PRINT_QR=false
TZ=America/Sao_Paulo

# Configurações do ambiente
ENVIRONMENT=production
"""

            with open(env_file, "w", encoding="utf-8") as f:
                f.write(env_content)

            self.log(
                "Arquivo .env criado. Configure suas chaves de API antes de iniciar."
            )

    def save_config(self):
        """Salva configurações do instalador"""
        config = {
            "version": self.version,
            "install_date": datetime.now().isoformat(),
            "install_dir": str(self.install_dir),
        }

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def load_config(self) -> dict[str, Any]:
        """Carrega configurações do instalador"""
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def install_or_update(self):
        """Instala ou atualiza a aplicação"""

        def run_install():
            try:
                self.install_btn.config(state=tk.DISABLED)
                self.update_progress(0)

                # Verificar Docker
                if not self.check_docker_installed():
                    if not self.install_docker_desktop():
                        return

                if not self.check_docker_compose_installed():
                    messagebox.showerror(
                        "Erro",
                        "Docker Compose não encontrado. Instale o Docker Desktop.",
                    )
                    return

                self.update_progress(10)

                # Verificar atualizações
                update_info = self.check_for_updates()
                self.update_progress(20)

                # Baixar e instalar
                if self.download_and_extract():
                    self.update_progress(80)

                    # Criar arquivo .env
                    self.create_env_file()
                    self.update_progress(90)

                    # Salvar configurações
                    self.save_config()
                    self.update_progress(100)

                    self.log("Instalação concluída com sucesso!")
                    self.update_status("Instalado - Pronto para usar")

                    # Habilitar botões
                    self.start_btn.config(state=tk.NORMAL)
                    self.open_btn.config(state=tk.NORMAL)

                    messagebox.showinfo(
                        "Sucesso",
                        "Instalação concluída! Configure o arquivo .env antes de iniciar.",
                    )
                else:
                    self.update_status("Erro na instalação")

            except Exception as e:
                self.log(f"Erro durante instalação: {e!s}")
                self.update_status("Erro na instalação")
                messagebox.showerror("Erro", f"Erro durante instalação: {e!s}")
            finally:
                self.install_btn.config(state=tk.NORMAL)

        # Executar em thread separada
        threading.Thread(target=run_install, daemon=True).start()

    def start_services(self):
        """Inicia os serviços Docker"""

        def run_start():
            try:
                self.start_btn.config(state=tk.DISABLED)
                self.update_status("Iniciando serviços...")

                os.chdir(self.install_dir)

                self.log("Iniciando containers Docker...")
                result = subprocess.run(
                    ["docker", "compose", "up", "-d"],
                    capture_output=True,
                    text=True,
                    cwd=self.install_dir,
                )

                if result.returncode == 0:
                    self.log("Serviços iniciados com sucesso!")
                    self.log(result.stdout)
                    self.update_status("Serviços em execução")
                    self.is_running = True

                    self.stop_btn.config(state=tk.NORMAL)
                    self.open_btn.config(state=tk.NORMAL)

                    # Aguardar um pouco para os serviços iniciarem
                    time.sleep(5)
                    self.check_services_status()

                else:
                    self.log(f"Erro ao iniciar serviços: {result.stderr}")
                    self.update_status("Erro ao iniciar")
                    messagebox.showerror(
                        "Erro", f"Erro ao iniciar serviços:\n{result.stderr}"
                    )

            except Exception as e:
                self.log(f"Erro ao iniciar serviços: {e!s}")
                self.update_status("Erro ao iniciar")
                messagebox.showerror("Erro", f"Erro ao iniciar serviços: {e!s}")
            finally:
                self.start_btn.config(state=tk.NORMAL)

        threading.Thread(target=run_start, daemon=True).start()

    def stop_services(self):
        """Para os serviços Docker"""

        def run_stop():
            try:
                self.stop_btn.config(state=tk.DISABLED)
                self.update_status("Parando serviços...")

                self.log("Parando containers Docker...")
                result = subprocess.run(
                    ["docker", "compose", "down"],
                    capture_output=True,
                    text=True,
                    cwd=self.install_dir,
                )

                if result.returncode == 0:
                    self.log("Serviços parados com sucesso!")
                    self.update_status("Serviços parados")
                    self.is_running = False

                    self.start_btn.config(state=tk.NORMAL)
                    self.open_btn.config(state=tk.DISABLED)

                else:
                    self.log(f"Erro ao parar serviços: {result.stderr}")
                    self.update_status("Erro ao parar")

            except Exception as e:
                self.log(f"Erro ao parar serviços: {e!s}")
                self.update_status("Erro ao parar")
            finally:
                self.stop_btn.config(state=tk.NORMAL)

        threading.Thread(target=run_stop, daemon=True).start()

    def check_services_status(self):
        """Verifica o status dos serviços"""
        try:
            result = subprocess.run(
                ["docker", "compose", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                cwd=self.install_dir,
            )

            if result.returncode == 0 and result.stdout.strip():
                services = []
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        try:
                            service = json.loads(line)
                            services.append(service)
                        except:
                            pass

                running_services = [s for s in services if s.get("State") == "running"]
                self.log(
                    f"Serviços em execução: {len(running_services)}/{len(services)}"
                )

                for service in services:
                    name = service.get("Service", "unknown")
                    state = service.get("State", "unknown")
                    self.log(f"  {name}: {state}")

        except Exception as e:
            self.log(f"Erro ao verificar status dos serviços: {e!s}")

    def open_interface(self):
        """Abre a interface web do Streamlit"""
        url = "http://localhost:8501"
        self.log(f"Abrindo interface web: {url}")
        webbrowser.open(url)

    def uninstall(self):
        """Desinstala a aplicação"""
        if messagebox.askyesno(
            "Confirmar", "Tem certeza que deseja desinstalar o Repense Assistente?"
        ):
            try:
                # Parar serviços se estiverem rodando
                if self.is_running:
                    self.stop_services()
                    time.sleep(3)

                # Remover containers e imagens
                self.log("Removendo containers e imagens Docker...")
                subprocess.run(
                    ["docker", "compose", "down", "--rmi", "all", "--volumes"],
                    cwd=self.install_dir,
                    capture_output=True,
                )

                # Remover diretório de instalação
                if self.install_dir.exists():
                    self.log("Removendo arquivos de instalação...")
                    shutil.rmtree(self.install_dir)

                self.log("Desinstalação concluída!")
                messagebox.showinfo(
                    "Sucesso", "Repense Assistente foi desinstalado com sucesso!"
                )

                # Fechar aplicação
                self.root.quit()

            except Exception as e:
                self.log(f"Erro durante desinstalação: {e!s}")
                messagebox.showerror("Erro", f"Erro durante desinstalação: {e!s}")

    def check_initial_status(self):
        """Verifica o status inicial da aplicação"""
        config = self.load_config()

        if config and self.install_dir.exists():
            self.log("Instalação existente encontrada")
            self.update_status("Instalado")
            self.start_btn.config(state=tk.NORMAL)

            # Verificar se os serviços estão rodando
            try:
                result = subprocess.run(
                    ["docker", "compose", "ps", "-q"],
                    capture_output=True,
                    text=True,
                    cwd=self.install_dir,
                )

                if result.returncode == 0 and result.stdout.strip():
                    self.log("Serviços já estão em execução")
                    self.update_status("Serviços em execução")
                    self.is_running = True
                    self.stop_btn.config(state=tk.NORMAL)
                    self.open_btn.config(state=tk.NORMAL)
                    self.check_services_status()

            except:
                pass
        else:
            self.log("Nenhuma instalação encontrada")
            self.update_status("Não instalado")

    def run(self):
        """Executa o instalador"""
        self.setup_gui()
        self.log(f"Iniciando {self.app_name} Installer v{self.version}")
        self.root.mainloop()


if __name__ == "__main__":
    installer = RepensenAssistenteInstaller()
    installer.run()
