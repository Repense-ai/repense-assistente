import json
import os
import sys
import threading
import time
import tkinter as tk
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import messagebox

import requests


class AutoUpdater:
    def __init__(self, config_file: str = None):
        self.config_file = config_file or str(
            Path.home() / "RepensenAssistente" / "updater_config.json"
        )
        self.github_repo = (
            "seu-usuario/repense-assistente"  # Substitua pelo seu repositório
        )
        self.github_api_url = (
            f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        )
        self.current_version = "1.0.0"
        self.check_interval = 24 * 60 * 60  # 24 horas em segundos
        self.running = False
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Carrega configurações do atualizador"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass

        # Configuração padrão
        return {
            "auto_check": True,
            "last_check": None,
            "notify_updates": True,
            "auto_download": False,
            "current_version": self.current_version,
        }

    def save_config(self):
        """Salva configurações do atualizador"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")

    def check_for_updates(self) -> dict:
        """Verifica se há atualizações disponíveis"""
        try:
            response = requests.get(self.github_api_url, timeout=10)

            if response.status_code == 200:
                release_info = response.json()
                latest_version = release_info.get("tag_name", "").lstrip("v")

                if self.is_newer_version(latest_version, self.current_version):
                    return {
                        "available": True,
                        "version": latest_version,
                        "release_info": release_info,
                    }
                else:
                    return {"available": False}
            else:
                return {"available": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            return {"available": False, "error": str(e)}

    def is_newer_version(self, latest: str, current: str) -> bool:
        """Compara versões para determinar se há uma mais nova"""
        try:
            latest_parts = [int(x) for x in latest.split(".")]
            current_parts = [int(x) for x in current.split(".")]

            # Normalizar tamanhos
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))

            return latest_parts > current_parts
        except:
            return False

    def show_update_notification(self, update_info: dict):
        """Mostra notificação de atualização disponível"""

        def show_dialog():
            root = tk.Tk()
            root.withdraw()  # Esconder janela principal

            version = update_info.get("version", "unknown")
            release_info = update_info.get("release_info", {})
            release_notes = release_info.get(
                "body", "Nenhuma nota de versão disponível."
            )

            message = (
                f"Nova versão disponível: {version}\n\n"
                f"Versão atual: {self.current_version}\n\n"
                f"Notas da versão:\n{release_notes[:200]}{'...' if len(release_notes) > 200 else ''}\n\n"
                "Deseja baixar e instalar a atualização agora?"
            )

            result = messagebox.askyesno(
                "Atualização Disponível", message, icon="question"
            )

            if result:
                self.download_and_install_update(update_info)

            root.destroy()

        # Executar em thread separada para não bloquear
        threading.Thread(target=show_dialog, daemon=True).start()

    def download_and_install_update(self, update_info: dict):
        """Baixa e instala a atualização"""
        try:
            # Abrir página de download
            release_info = update_info.get("release_info", {})
            download_url = release_info.get(
                "html_url", f"https://github.com/{self.github_repo}/releases/latest"
            )

            webbrowser.open(download_url)

            # Mostrar instruções
            root = tk.Tk()
            root.withdraw()

            messagebox.showinfo(
                "Download da Atualização",
                "A página de download foi aberta no seu navegador.\n\n"
                "Baixe o novo instalador e execute-o para atualizar o Repense Assistente.\n\n"
                "O instalador detectará automaticamente a instalação existente e a atualizará.",
            )

            root.destroy()

        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro", f"Erro ao baixar atualização: {e}")
            root.destroy()

    def should_check_for_updates(self) -> bool:
        """Verifica se deve procurar por atualizações"""
        if not self.config.get("auto_check", True):
            return False

        last_check = self.config.get("last_check")
        if not last_check:
            return True

        try:
            last_check_date = datetime.fromisoformat(last_check)
            return datetime.now() - last_check_date > timedelta(
                seconds=self.check_interval
            )
        except:
            return True

    def update_last_check(self):
        """Atualiza timestamp da última verificação"""
        self.config["last_check"] = datetime.now().isoformat()
        self.save_config()

    def run_update_check(self):
        """Executa verificação de atualização"""
        if not self.should_check_for_updates():
            return

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Verificando atualizações...")

        update_info = self.check_for_updates()
        self.update_last_check()

        if update_info.get("available"):
            print(f"Nova versão disponível: {update_info.get('version')}")
            if self.config.get("notify_updates", True):
                self.show_update_notification(update_info)
        else:
            print("Nenhuma atualização disponível")
            if update_info.get("error"):
                print(f"Erro na verificação: {update_info['error']}")

    def start_background_checker(self):
        """Inicia verificador em segundo plano"""
        if self.running:
            return

        self.running = True

        def background_loop():
            while self.running:
                try:
                    self.run_update_check()
                except Exception as e:
                    print(f"Erro na verificação automática: {e}")

                # Aguardar próxima verificação
                for _ in range(self.check_interval):
                    if not self.running:
                        break
                    time.sleep(1)

        thread = threading.Thread(target=background_loop, daemon=True)
        thread.start()
        print("Verificador automático de atualizações iniciado")

    def stop_background_checker(self):
        """Para verificador em segundo plano"""
        self.running = False
        print("Verificador automático de atualizações parado")

    def create_settings_gui(self):
        """Cria interface para configurações do atualizador"""
        root = tk.Tk()
        root.title("Configurações do Atualizador")
        root.geometry("400x300")
        root.resizable(False, False)

        # Variáveis
        auto_check_var = tk.BooleanVar(value=self.config.get("auto_check", True))
        notify_updates_var = tk.BooleanVar(
            value=self.config.get("notify_updates", True)
        )
        auto_download_var = tk.BooleanVar(value=self.config.get("auto_download", False))

        # Frame principal
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = tk.Label(
            main_frame, text="Configurações do Atualizador", font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Opções
        auto_check_cb = tk.Checkbutton(
            main_frame,
            text="Verificar atualizações automaticamente",
            variable=auto_check_var,
        )
        auto_check_cb.pack(anchor=tk.W, pady=5)

        notify_updates_cb = tk.Checkbutton(
            main_frame,
            text="Notificar quando houver atualizações",
            variable=notify_updates_var,
        )
        notify_updates_cb.pack(anchor=tk.W, pady=5)

        auto_download_cb = tk.Checkbutton(
            main_frame,
            text="Baixar atualizações automaticamente (em desenvolvimento)",
            variable=auto_download_var,
            state=tk.DISABLED,
        )
        auto_download_cb.pack(anchor=tk.W, pady=5)

        # Informações
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=20)

        tk.Label(info_frame, text=f"Versão atual: {self.current_version}").pack(
            anchor=tk.W
        )

        last_check = self.config.get("last_check")
        if last_check:
            try:
                last_check_date = datetime.fromisoformat(last_check)
                last_check_str = last_check_date.strftime("%d/%m/%Y %H:%M")
            except:
                last_check_str = "Desconhecido"
        else:
            last_check_str = "Nunca"

        tk.Label(info_frame, text=f"Última verificação: {last_check_str}").pack(
            anchor=tk.W
        )

        # Botões
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)

        def save_settings():
            self.config["auto_check"] = auto_check_var.get()
            self.config["notify_updates"] = notify_updates_var.get()
            self.config["auto_download"] = auto_download_var.get()
            self.save_config()

            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            root.destroy()

        def check_now():
            self.run_update_check()
            messagebox.showinfo("Verificação", "Verificação de atualizações concluída!")

        tk.Button(button_frame, text="Verificar Agora", command=check_now).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(button_frame, text="Salvar", command=save_settings).pack(
            side=tk.RIGHT, padx=5
        )
        tk.Button(button_frame, text="Cancelar", command=root.destroy).pack(
            side=tk.RIGHT
        )

        root.mainloop()


def main():
    """Função principal do atualizador"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--settings":
            updater = AutoUpdater()
            updater.create_settings_gui()
        elif sys.argv[1] == "--check":
            updater = AutoUpdater()
            updater.run_update_check()
        elif sys.argv[1] == "--daemon":
            updater = AutoUpdater()
            updater.start_background_checker()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                updater.stop_background_checker()
    else:
        # Modo interativo
        updater = AutoUpdater()
        print("=== Atualizador do Repense Assistente ===")
        print("1. Verificar atualizações agora")
        print("2. Configurações")
        print("3. Iniciar verificação automática")
        print("0. Sair")

        while True:
            try:
                choice = input("\nEscolha uma opção: ").strip()

                if choice == "1":
                    updater.run_update_check()
                elif choice == "2":
                    updater.create_settings_gui()
                elif choice == "3":
                    updater.start_background_checker()
                    print("Pressione Ctrl+C para parar...")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        updater.stop_background_checker()
                elif choice == "0":
                    break
                else:
                    print("Opção inválida!")

            except KeyboardInterrupt:
                break

        print("Atualizador encerrado.")


if __name__ == "__main__":
    main()
