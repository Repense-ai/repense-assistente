import json
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

# Adicionar o diretório do updater ao path
sys.path.append(str(Path(__file__).parent))

try:
    from updater import AutoUpdater
except ImportError:
    print("Módulo updater não encontrado")
    sys.exit(1)


class StartupManager:
    def __init__(self):
        self.install_dir = Path.home() / "RepensenAssistente"
        self.config_file = self.install_dir / "startup_config.json"
        self.updater = AutoUpdater()
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Carrega configurações de inicialização"""
        try:
            if self.config_file.exists():
                with open(self.config_file, encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass

        return {
            "auto_start_services": False,
            "check_updates_on_startup": True,
            "minimize_to_tray": True,
            "startup_delay": 30,  # segundos
        }

    def save_config(self):
        """Salva configurações de inicialização"""
        try:
            self.install_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")

    def is_docker_running(self) -> bool:
        """Verifica se o Docker está rodando"""
        try:
            result = subprocess.run(
                ["docker", "info"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except:
            return False

    def are_services_running(self) -> bool:
        """Verifica se os serviços do Repense Assistente estão rodando"""
        try:
            if not self.install_dir.exists():
                return False

            result = subprocess.run(
                ["docker", "compose", "ps", "-q"],
                capture_output=True,
                text=True,
                cwd=self.install_dir,
                timeout=10,
            )

            return result.returncode == 0 and result.stdout.strip()
        except:
            return False

    def start_services(self) -> bool:
        """Inicia os serviços do Repense Assistente"""
        try:
            if not self.install_dir.exists():
                print("Diretório de instalação não encontrado")
                return False

            print("Iniciando serviços do Repense Assistente...")
            result = subprocess.run(
                ["docker", "compose", "up", "-d"],
                capture_output=True,
                text=True,
                cwd=self.install_dir,
                timeout=120,
            )

            if result.returncode == 0:
                print("Serviços iniciados com sucesso")
                return True
            else:
                print(f"Erro ao iniciar serviços: {result.stderr}")
                return False

        except Exception as e:
            print(f"Erro ao iniciar serviços: {e}")
            return False

    def show_startup_notification(
        self, message: str, title: str = "Repense Assistente"
    ):
        """Mostra notificação de inicialização"""

        def show_notification():
            root = tk.Tk()
            root.withdraw()

            messagebox.showinfo(title, message)
            root.destroy()

        threading.Thread(target=show_notification, daemon=True).start()

    def run_startup_sequence(self):
        """Executa sequência de inicialização"""
        print("=== Repense Assistente - Inicialização ===")

        # Aguardar delay configurado
        delay = self.config.get("startup_delay", 30)
        if delay > 0:
            print(f"Aguardando {delay} segundos antes de iniciar...")
            time.sleep(delay)

        # Verificar se Docker está rodando
        if not self.is_docker_running():
            print("Docker não está rodando. Aguardando...")

            # Aguardar até 2 minutos pelo Docker
            for i in range(24):  # 24 * 5 = 120 segundos
                time.sleep(5)
                if self.is_docker_running():
                    print("Docker detectado!")
                    break
            else:
                print("Docker não foi detectado. Abortando inicialização.")
                self.show_startup_notification(
                    "Docker não foi detectado. Inicie o Docker Desktop manualmente.",
                    "Erro de Inicialização",
                )
                return

        # Verificar atualizações se configurado
        if self.config.get("check_updates_on_startup", True):
            print("Verificando atualizações...")
            try:
                self.updater.run_update_check()
            except Exception as e:
                print(f"Erro ao verificar atualizações: {e}")

        # Iniciar serviços se configurado
        if self.config.get("auto_start_services", False):
            if not self.are_services_running():
                print("Iniciando serviços automaticamente...")
                if self.start_services():
                    self.show_startup_notification(
                        "Repense Assistente iniciado com sucesso!\n\nAcesse: http://localhost:8501",
                        "Serviços Iniciados",
                    )
                else:
                    self.show_startup_notification(
                        "Erro ao iniciar serviços do Repense Assistente.\nVerifique os logs para mais detalhes.",
                        "Erro de Inicialização",
                    )
            else:
                print("Serviços já estão rodando")

        print("Inicialização concluída")

    def create_settings_gui(self):
        """Cria interface para configurações de inicialização"""
        root = tk.Tk()
        root.title("Configurações de Inicialização")
        root.geometry("450x350")
        root.resizable(False, False)

        # Variáveis
        auto_start_var = tk.BooleanVar(
            value=self.config.get("auto_start_services", False)
        )
        check_updates_var = tk.BooleanVar(
            value=self.config.get("check_updates_on_startup", True)
        )
        minimize_tray_var = tk.BooleanVar(
            value=self.config.get("minimize_to_tray", True)
        )
        delay_var = tk.IntVar(value=self.config.get("startup_delay", 30))

        # Frame principal
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = tk.Label(
            main_frame,
            text="Configurações de Inicialização",
            font=("Arial", 14, "bold"),
        )
        title_label.pack(pady=(0, 20))

        # Opções
        auto_start_cb = tk.Checkbutton(
            main_frame,
            text="Iniciar serviços automaticamente no startup",
            variable=auto_start_var,
        )
        auto_start_cb.pack(anchor=tk.W, pady=5)

        check_updates_cb = tk.Checkbutton(
            main_frame,
            text="Verificar atualizações na inicialização",
            variable=check_updates_var,
        )
        check_updates_cb.pack(anchor=tk.W, pady=5)

        minimize_tray_cb = tk.Checkbutton(
            main_frame,
            text="Minimizar para bandeja do sistema",
            variable=minimize_tray_var,
            state=tk.DISABLED,  # Funcionalidade futura
        )
        minimize_tray_cb.pack(anchor=tk.W, pady=5)

        # Delay de inicialização
        delay_frame = tk.Frame(main_frame)
        delay_frame.pack(fill=tk.X, pady=10)

        tk.Label(delay_frame, text="Delay de inicialização (segundos):").pack(
            side=tk.LEFT
        )
        delay_spinbox = tk.Spinbox(
            delay_frame, from_=0, to=300, textvariable=delay_var, width=10
        )
        delay_spinbox.pack(side=tk.RIGHT)

        # Informações
        info_frame = tk.LabelFrame(main_frame, text="Informações", padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=20)

        docker_status = "Rodando" if self.is_docker_running() else "Parado"
        tk.Label(info_frame, text=f"Status do Docker: {docker_status}").pack(
            anchor=tk.W
        )

        services_status = "Rodando" if self.are_services_running() else "Parado"
        tk.Label(info_frame, text=f"Status dos Serviços: {services_status}").pack(
            anchor=tk.W
        )

        install_status = "Instalado" if self.install_dir.exists() else "Não instalado"
        tk.Label(info_frame, text=f"Status da Instalação: {install_status}").pack(
            anchor=tk.W
        )

        # Botões
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)

        def save_settings():
            self.config["auto_start_services"] = auto_start_var.get()
            self.config["check_updates_on_startup"] = check_updates_var.get()
            self.config["minimize_to_tray"] = minimize_tray_var.get()
            self.config["startup_delay"] = delay_var.get()
            self.save_config()

            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            root.destroy()

        def test_startup():
            messagebox.showinfo("Teste", "Executando sequência de inicialização...")
            threading.Thread(target=self.run_startup_sequence, daemon=True).start()

        def install_startup():
            """Instala o script no startup do Windows"""
            try:
                startup_folder = (
                    Path.home()
                    / "AppData"
                    / "Roaming"
                    / "Microsoft"
                    / "Windows"
                    / "Start Menu"
                    / "Programs"
                    / "Startup"
                )
                startup_script = startup_folder / "RepensenAssistente-Startup.bat"

                script_content = f"""@echo off
cd /d "{Path(__file__).parent}"
python "{__file__}" --startup
"""

                with open(startup_script, "w") as f:
                    f.write(script_content)

                messagebox.showinfo(
                    "Sucesso", "Script de inicialização instalado com sucesso!"
                )

            except Exception as e:
                messagebox.showerror(
                    "Erro", f"Erro ao instalar script de inicialização: {e}"
                )

        tk.Button(button_frame, text="Testar Inicialização", command=test_startup).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(
            button_frame, text="Instalar no Startup", command=install_startup
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Salvar", command=save_settings).pack(
            side=tk.RIGHT, padx=5
        )
        tk.Button(button_frame, text="Cancelar", command=root.destroy).pack(
            side=tk.RIGHT
        )

        root.mainloop()


def main():
    """Função principal"""
    startup_manager = StartupManager()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--startup":
            # Modo de inicialização automática
            startup_manager.run_startup_sequence()
        elif sys.argv[1] == "--settings":
            # Modo de configurações
            startup_manager.create_settings_gui()
        elif sys.argv[1] == "--install":
            # Instalar no startup
            try:
                startup_folder = (
                    Path.home()
                    / "AppData"
                    / "Roaming"
                    / "Microsoft"
                    / "Windows"
                    / "Start Menu"
                    / "Programs"
                    / "Startup"
                )
                startup_script = startup_folder / "RepensenAssistente-Startup.bat"

                script_content = f"""@echo off
cd /d "{Path(__file__).parent}"
python "{__file__}" --startup
"""

                with open(startup_script, "w") as f:
                    f.write(script_content)

                print("Script de inicialização instalado com sucesso!")

            except Exception as e:
                print(f"Erro ao instalar script de inicialização: {e}")
        else:
            print("Uso: python startup.py [--startup|--settings|--install]")
    else:
        # Modo interativo
        print("=== Gerenciador de Inicialização ===")
        print("1. Executar sequência de inicialização")
        print("2. Configurações")
        print("3. Instalar no startup do Windows")
        print("0. Sair")

        while True:
            try:
                choice = input("\nEscolha uma opção: ").strip()

                if choice == "1":
                    startup_manager.run_startup_sequence()
                elif choice == "2":
                    startup_manager.create_settings_gui()
                elif choice == "3":
                    # Instalar no startup
                    try:
                        startup_folder = (
                            Path.home()
                            / "AppData"
                            / "Roaming"
                            / "Microsoft"
                            / "Windows"
                            / "Start Menu"
                            / "Programs"
                            / "Startup"
                        )
                        startup_script = (
                            startup_folder / "RepensenAssistente-Startup.bat"
                        )

                        script_content = f"""@echo off
cd /d "{Path(__file__).parent}"
python "{__file__}" --startup
"""

                        with open(startup_script, "w") as f:
                            f.write(script_content)

                        print("Script de inicialização instalado com sucesso!")

                    except Exception as e:
                        print(f"Erro ao instalar script de inicialização: {e}")
                elif choice == "0":
                    break
                else:
                    print("Opção inválida!")

            except KeyboardInterrupt:
                break

        print("Gerenciador encerrado.")


if __name__ == "__main__":
    main()
