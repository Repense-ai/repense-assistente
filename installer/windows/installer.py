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
from tkinter import messagebox, scrolledtext, simpledialog, ttk
from typing import Any

import requests
import redis

# Documentação integrada
DOCKER_INSTALLATION_GUIDE = """
INSTALAÇÃO DO DOCKER DESKTOP - PASSO A PASSO

O Docker Desktop é necessário para executar o Repense Assistente. 
Siga estes passos para instalá-lo:

1. DOWNLOAD:
   • Acesse: https://www.docker.com/products/docker-desktop/
   • Clique em "Download for Windows"
   • Aguarde o download do arquivo "Docker Desktop Installer.exe"

2. INSTALAÇÃO:
   • Execute o arquivo baixado como administrador
   • Aceite os termos de licença
   • Mantenha as opções padrão selecionadas
   • Clique em "Install" e aguarde a instalação
   • Reinicie o computador quando solicitado

3. CONFIGURAÇÃO INICIAL:
   • Após reiniciar, o Docker Desktop será iniciado automaticamente
   • Aceite os termos de serviço
   • Opcionalmente, crie uma conta Docker Hub (não obrigatório)
   • Aguarde o Docker finalizar a inicialização

4. VERIFICAÇÃO:
   • Procure o ícone da "baleia" na bandeja do sistema (próximo ao relógio)
   • O ícone deve estar azul/verde, indicando que o Docker está rodando
   • Se estiver cinza, clique nele para iniciar o Docker

5. TESTE:
   • Abra o Prompt de Comando (cmd)
   • Digite: docker --version
   • Se aparecer a versão do Docker, a instalação foi bem-sucedida

REQUISITOS MÍNIMOS:
• Windows 10 versão 2004 ou superior (Build 19041)
• WSL 2 (será instalado automaticamente)
• Virtualização habilitada no BIOS
• 4GB de RAM (recomendado 8GB)

PROBLEMAS COMUNS:
• Erro de WSL: Execute "wsl --install" no PowerShell como administrador
• Virtualização desabilitada: Acesse o BIOS e habilite VT-x/AMD-V
• Docker não inicia: Reinicie o serviço do Docker Desktop

Após instalar o Docker, volte a este instalador e clique em "Instalar/Atualizar".
"""

USER_DOCUMENTATION = """
REPENSE ASSISTENTE - DOCUMENTAÇÃO COMPLETA

═══════════════════════════════════════════════════════════════

📋 ÍNDICE:
1. Introdução
2. Pré-requisitos
3. Como Usar o Instalador
4. Configuração da API OpenAI
5. Acessos e URLs
6. Solução de Problemas
7. Funcionalidades Avançadas
8. Suporte

═══════════════════════════════════════════════════════════════

1. INTRODUÇÃO

O Repense Assistente é uma plataforma de IA para atendimento automatizado 
via WhatsApp. Esta ferramenta permite:

✅ Atendimento automatizado 24/7
✅ Integração com WhatsApp Web
✅ Interface web intuitiva
✅ API para integrações customizadas
✅ Banco de dados Redis para persistência

═══════════════════════════════════════════════════════════════

2. PRÉ-REQUISITOS

SISTEMA OPERACIONAL:
• Windows 10 versão 2004 ou superior
• Windows 11 (recomendado)

SOFTWARE NECESSÁRIO:
• Docker Desktop (será orientada a instalação se necessário)
• Conexão com internet estável
• Navegador web moderno (Chrome, Firefox, Edge)

RECURSOS MÍNIMOS:
• 4GB de RAM (8GB recomendado)
• 10GB de espaço em disco
• Processador dual-core

CHAVES DE API:
• OpenAI API Key (obrigatório)
• Outras integrações conforme necessário

═══════════════════════════════════════════════════════════════

3. COMO USAR O INSTALADOR

PRIMEIRO USO:

1. Execute este instalador como ADMINISTRADOR
2. Clique em "Instalar/Atualizar"
3. Aguarde o download e instalação dos componentes
4. Clique em "Iniciar Serviços"
5. Configure sua chave OpenAI
6. Clique em "Abrir Interface"

BOTÕES PRINCIPAIS:

• Instalar/Atualizar: Baixa e instala a versão mais recente
• Iniciar Serviços: Liga todos os containers Docker
• Parar Serviços: Para todos os containers Docker
• Abrir Interface: Abre a interface web (localhost:8501)
• Conectar WhatsApp: Acessa configuração do WhatsApp
• Documentação: Exibe esta ajuda
• Desinstalar: Remove completamente o sistema

ATUALIZAÇÕES:
O instalador verifica automaticamente por atualizações no GitHub
e notifica quando há versões mais recentes disponíveis.

═══════════════════════════════════════════════════════════════

4. CONFIGURAÇÃO DA API OPENAI

A chave da OpenAI é essencial para o funcionamento do assistente.

COMO OBTER A CHAVE:
1. Acesse: https://platform.openai.com/api-keys
2. Faça login na sua conta OpenAI
3. Clique em "Create new secret key"
4. Copie a chave gerada (começa com "sk-")

COMO CONFIGURAR NO INSTALADOR:
1. Com os serviços rodando, a configuração é automática via interface
2. A chave é armazenada com segurança no Redis
3. Não é necessário editar arquivos manualmente

IMPORTANTE:
• Mantenha sua chave em segurança
• Não compartilhe com terceiros
• Monitore o uso na plataforma OpenAI
• Configure limites de gastos se necessário

═══════════════════════════════════════════════════════════════

5. ACESSOS E URLS

Após iniciar os serviços, os seguintes endereços ficam disponíveis:

INTERFACE PRINCIPAL:
• URL: http://localhost:8501
• Descrição: Interface web principal do Repense Assistente
• Use: Configurações, conversas, análises

API BACKEND:
• URL: http://localhost:8000
• Descrição: API REST para integrações
• Docs: http://localhost:8000/docs (Swagger)

WHATSAPP (WAHA):
• URL: http://localhost:3000
• Descrição: Interface para configurar WhatsApp
• Use: Conectar/desconectar WhatsApp Web

REDIS:
• Host: localhost
• Porta: 6380
• Descrição: Banco de dados para configurações

═══════════════════════════════════════════════════════════════

6. SOLUÇÃO DE PROBLEMAS

DOCKER NÃO ENCONTRADO:
• Instale o Docker Desktop
• Reinicie o computador
• Verifique se o ícone da "baleia" está na bandeja

ERRO DE PERMISSÕES:
• Execute sempre como administrador
• Desabilite antivírus temporariamente
• Verifique permissões da pasta do usuário

SERVIÇOS NÃO INICIAM:
• Verifique se as portas estão livres (3000, 6380, 8000, 8501)
• Reinicie o Docker Desktop
• Verifique logs no instalador

PORTAS EM USO:
Execute no cmd para verificar:
netstat -ano | findstr ":8501"
netstat -ano | findstr ":8000"
netstat -ano | findstr ":3000"
netstat -ano | findstr ":6380"

PERFORMANCE LENTA:
• Aumente recursos do Docker (Settings > Resources)
• Feche programas desnecessários
• Verifique espaço em disco

ERRO DE CONFIGURAÇÃO:
• Verifique se a chave OpenAI está correta
• Confirme se o Redis está rodando
• Reinicie os serviços se necessário

CONTAINERS NÃO RESPONDEM:
1. Pare os serviços
2. Execute: docker system prune -f
3. Reinicie os serviços

═══════════════════════════════════════════════════════════════

7. FUNCIONALIDADES AVANÇADAS

LOGS E MONITORAMENTO:
• Logs são exibidos em tempo real no instalador
• Para logs detalhados: docker compose logs
• Para um serviço específico: docker compose logs [nome_servico]

BACKUP E RESTAURAÇÃO:
• Configurações ficam em: %USERPROFILE%\\RepensenAssistente
• Backup do Redis: docker exec redis redis-cli save
• Dados persistem entre reinicializações

CUSTOMIZAÇÕES:
• Arquivos de configuração em: %USERPROFILE%\\RepensenAssistente
• docker-compose.yml pode ser editado para customizações
• Variáveis de ambiente no arquivo .env

INTEGRAÇÕES:
• API disponível em localhost:8000/docs
• Webhook para WhatsApp configurável
• Suporte a múltiplos formatos de dados

═══════════════════════════════════════════════════════════════

8. SUPORTE

DOCUMENTAÇÃO TÉCNICA:
• GitHub: https://github.com/Repense-ai/repense-assistente
• Issues: Reporte problemas no GitHub

LOGS IMPORTANTES:
Sempre inclua os seguintes logs ao reportar problemas:
• Logs do instalador (visíveis na interface)
• docker compose logs (no terminal)
• Versão do Windows e Docker

ANTES DE REPORTAR:
1. Verifique se o Docker está rodando
2. Confirme que tem a versão mais recente
3. Tente reinstalar se necessário
4. Verifique se as portas estão livres

INFORMAÇÕES DO SISTEMA:
Para suporte, tenha em mãos:
• Versão do Windows (winver)
• Versão do Docker (docker --version)
• Logs de erro específicos
• Passos para reproduzir o problema

═══════════════════════════════════════════════════════════════

VERSÃO DA DOCUMENTAÇÃO: 1.0.0
ÚLTIMA ATUALIZAÇÃO: """ + datetime.now().strftime("%d/%m/%Y") + """

Para mais informações, visite:
https://github.com/Repense-ai/repense-assistente
"""


class RepensenAssistenteInstaller:
    def __init__(self):
        self.app_name = "repense-assistente"
        self.version = "1.0.0"
        # O repositório GitHub é usado para verificar atualizações.
        self.github_repo = "Repense-ai/repense-assistente"
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

        # Conexão com Redis
        self.redis_client = None

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

        # Apply a theme
        style = ttk.Style(self.root)
        style.theme_use("clam")

        # Variáveis de controle
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Pronto para instalar")

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Título
        title_label = ttk.Label(
            main_frame, text=self.app_name, font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        # --- Status and Progress ---
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        status_frame.columnconfigure(1, weight=1)

        ttk.Label(status_frame, text="Status:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W
        )
        ttk.Label(status_frame, textvariable=self.status_var).grid(
            row=0, column=1, sticky=tk.W
        )
        ttk.Label(status_frame, text="Progresso:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=(5, 0)
        )
        self.progress_bar = ttk.Progressbar(
            status_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.grid(
            row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0), padx=5
        )

        # --- Button Frames ---
        button_container = ttk.Frame(main_frame, padding=(0, 20))
        button_container.grid(row=2, column=0, sticky=(tk.W, tk.E))
        button_container.columnconfigure(0, weight=1)

        # --- Main Actions ---
        actions_frame = ttk.LabelFrame(
            button_container, text="Ações Principais", padding="10"
        )
        actions_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        self.install_btn = ttk.Button(
            actions_frame, text="Instalar/Atualizar", command=self.install_or_update
        )
        self.install_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.start_btn = ttk.Button(
            actions_frame,
            text="Iniciar Serviços",
            command=self.start_services,
            state=tk.DISABLED,
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.stop_btn = ttk.Button(
            actions_frame,
            text="Parar Serviços",
            command=self.stop_services,
            state=tk.DISABLED,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # --- Application ---
        app_frame = ttk.LabelFrame(
            button_container, text="Aplicação", padding="10"
        )
        app_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        self.open_app_btn = ttk.Button(
            app_frame, text="Abrir Interface", command=self.open_interface, state=tk.DISABLED
        )
        self.open_app_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.whatsapp_btn = ttk.Button(
            app_frame,
            text="Conectar WhatsApp",
            command=self.open_whatsapp_config,
            state=tk.DISABLED,
        )
        self.whatsapp_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # --- Help and Administration ---
        admin_frame = ttk.LabelFrame(
            button_container, text="Ajuda e Administração", padding="10"
        )
        admin_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)

        self.help_btn = ttk.Button(
            admin_frame, text="Documentação", command=self.show_documentation
        )
        self.help_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.docker_help_btn = ttk.Button(
            admin_frame, text="Instalar Docker", command=self.show_docker_guide
        )
        self.docker_help_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.uninstall_btn = ttk.Button(
            admin_frame, text="Desinstalar", command=self.uninstall
        )
        self.uninstall_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # --- Log Area ---
        log_frame = ttk.LabelFrame(main_frame, text="Log de Atividades", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Verificar status inicial
        self.check_initial_status()

    def show_documentation(self):
        """Exibe a documentação completa em uma nova janela"""
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Documentação - Repense Assistente")
        doc_window.geometry("900x700")
        doc_window.resizable(True, True)

        # Frame principal
        main_frame = ttk.Frame(doc_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(
            main_frame, 
            text="📚 Documentação Completa", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Área de texto com scroll
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 10),
            bg="#f8f9fa",
            fg="#212529"
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, USER_DOCUMENTATION)
        text_widget.config(state=tk.DISABLED)

        # Botão para fechar
        close_btn = ttk.Button(
            main_frame, 
            text="Fechar", 
            command=doc_window.destroy
        )
        close_btn.pack(pady=(10, 0))

    def show_docker_guide(self):
        """Exibe o guia de instalação do Docker em uma nova janela"""
        docker_window = tk.Toplevel(self.root)
        docker_window.title("Guia de Instalação - Docker Desktop")
        docker_window.geometry("800x600")
        docker_window.resizable(True, True)

        # Frame principal
        main_frame = ttk.Frame(docker_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(
            main_frame, 
            text="🐳 Como Instalar o Docker Desktop", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Área de texto com scroll
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 10),
            bg="#f8f9fa",
            fg="#212529"
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, DOCKER_INSTALLATION_GUIDE)
        text_widget.config(state=tk.DISABLED)

        # Frame para botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Botão para abrir página do Docker
        download_btn = ttk.Button(
            button_frame, 
            text="🌐 Abrir Página de Download", 
            command=lambda: webbrowser.open("https://www.docker.com/products/docker-desktop/")
        )
        download_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Botão para verificar Docker
        check_btn = ttk.Button(
            button_frame, 
            text="🔍 Verificar Docker", 
            command=self.check_docker_from_guide
        )
        check_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Botão para fechar
        close_btn = ttk.Button(
            button_frame, 
            text="Fechar", 
            command=docker_window.destroy
        )
        close_btn.pack(side=tk.RIGHT)

    def check_docker_from_guide(self):
        """Verifica se o Docker está instalado a partir do guia"""
        if self.check_docker_installed() and self.check_docker_compose_installed():
            messagebox.showinfo(
                "Docker Detectado", 
                "✅ Docker Desktop foi detectado com sucesso!\n\n"
                "Agora você pode fechar esta janela e usar o instalador normalmente."
            )
        else:
            messagebox.showwarning(
                "Docker Não Detectado", 
                "❌ Docker Desktop ainda não foi detectado.\n\n"
                "Certifique-se de que:\n"
                "• O Docker Desktop foi instalado corretamente\n"
                "• O computador foi reiniciado após a instalação\n"
                "• O Docker Desktop está rodando (ícone da baleia na bandeja)\n\n"
                "Tente novamente após verificar estes pontos."
            )

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
        """Guia o usuário para instalar o Docker Desktop com instruções detalhadas"""
        message = (
            "🐳 DOCKER NÃO ENCONTRADO\n\n"
            "O Docker Desktop é necessário para executar o Repense Assistente.\n\n"
            "OPÇÕES:\n\n"
            "📖 Ver Guia Completo: Instruções detalhadas passo a passo\n"
            "🌐 Download Direto: Ir direto para a página de download\n"
            "❌ Cancelar: Sair sem instalar\n\n"
            "Recomendamos ver o guia completo primeiro."
        )

        # Criar janela customizada
        dialog = tk.Toplevel(self.root)
        dialog.title("Docker Não Encontrado")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Centralizar na tela
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"500x300+{x}+{y}")

        result = {"choice": None}

        # Frame principal
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Ícone e título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(
            title_frame, 
            text="🐳 Docker Desktop Necessário", 
            font=("Arial", 14, "bold")
        )
        title_label.pack()

        # Mensagem
        msg_label = ttk.Label(
            main_frame, 
            text=message, 
            wraplength=450,
            justify=tk.LEFT
        )
        msg_label.pack(pady=(0, 20))

        # Frame para botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        def set_choice(choice):
            result["choice"] = choice
            dialog.destroy()

        # Botões
        guide_btn = ttk.Button(
            button_frame, 
            text="📖 Ver Guia Completo", 
            command=lambda: set_choice("guide")
        )
        guide_btn.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        download_btn = ttk.Button(
            button_frame, 
            text="🌐 Download Direto", 
            command=lambda: set_choice("download")
        )
        download_btn.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        cancel_btn = ttk.Button(
            button_frame, 
            text="❌ Cancelar", 
            command=lambda: set_choice("cancel")
        )
        cancel_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Aguardar escolha
        dialog.wait_window()

        # Processar escolha
        if result["choice"] == "guide":
            self.show_docker_guide()
        elif result["choice"] == "download":
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

                # Remover arquivo .env se existir de uma instalação antiga
                old_env_file = self.install_dir / ".env"
                if old_env_file.exists():
                    self.log("Removendo arquivo .env antigo...")
                    old_env_file.unlink()

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

    def connect_to_redis(self):
        """Tenta conectar ao Redis"""
        try:
            self.log("Conectando ao Redis em localhost:6380...")
            self.redis_client = redis.Redis(host="localhost", port=6380, db=0, decode_responses=True)
            self.redis_client.ping()
            self.log("Conexão com Redis bem-sucedida.")
            return True
        except redis.exceptions.ConnectionError as e:
            self.log(f"Falha ao conectar ao Redis: {e}")
            self.redis_client = None
            return False

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

                if not self.check_docker_installed():
                    if not self.install_docker_desktop():
                        return
                if not self.check_docker_compose_installed():
                    messagebox.showerror(
                        "Erro", "Docker Compose não encontrado. Instale o Docker Desktop."
                    )
                    return
                self.update_progress(10)

                self.check_for_updates()
                self.update_progress(20)

                if self.download_and_extract():
                    self.update_progress(80)
                    self.log("Forçando reconstrução dos serviços após a atualização...")
                    self.update_status("Reconstruindo imagens...")
                    if not self.rebuild_services(from_install=True):
                        raise Exception("Falha ao reconstruir as imagens Docker.")
                    
                    self.save_config()
                    self.update_progress(100)
                    self.log("Instalação e atualização concluídas!")
                    self.update_status("Instalado - Pronto para usar")
                    messagebox.showinfo(
                        "Sucesso",
                        "Aplicação instalada/atualizada com sucesso! "
                        "Serviços reconstruídos e prontos para iniciar.",
                    )
                else:
                    self.update_status("Erro na instalação")

            except Exception as e:
                self.log(f"Erro durante instalação: {e!s}")
                self.update_status("Erro na instalação")
                messagebox.showerror("Erro", f"Erro durante instalação: {e!s}")
            finally:
                self.install_btn.config(state=tk.NORMAL)
                self.check_initial_status()

        threading.Thread(target=run_install, daemon=True).start()

    def rebuild_services(self, from_install=False):
        """Reconstrói as imagens Docker e reinicia os serviços"""
        if not from_install and not messagebox.askyesno(
            "Confirmar Reconstrução",
            "Isso irá reconstruir todas as imagens e reiniciar os serviços. "
            "Pode levar vários minutos. Deseja continuar?",
        ):
            return False
        
        rebuild_success = False
        try:
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
            self.update_status("Reconstruindo imagens...")

            self.log("Parando serviços antes de reconstruir...")
            self.stop_services(from_rebuild=True)
            time.sleep(5)

            self.log("Iniciando reconstrução das imagens (build --no-cache --pull)...")
            process = subprocess.Popen(
                ["docker", "compose", "build", "--no-cache", "--pull"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.install_dir,
                encoding="utf-8",
                errors="replace",
            )
            while True:
                line = process.stdout.readline()
                if not line: break
                self.log(line.strip())
            process.wait()

            if process.returncode == 0:
                self.log("Imagens reconstruídas com sucesso!")
                self.update_status("Reconstrução concluída.")
                rebuild_success = True
                if not from_install:
                    self.log("Reiniciando serviços após a reconstrução...")
                    self.update_status("Reiniciando serviços...")
                    self.start_services()
            else:
                self.log("Erro durante a reconstrução das imagens.")
                self.update_status("Erro na reconstrução.")

        except Exception as e:
            self.log(f"Erro durante reconstrução: {e!s}")
            self.update_status("Erro na reconstrução")
        
        if rebuild_success and not from_install:
            self.log("Reconstrução e reinicialização concluídas!")
        elif rebuild_success:
            self.log("Reconstrução concluída!")

        return rebuild_success

    def start_services(self):
        """Inicia os serviços Docker e transmite o output."""

        def run_start():
            try:
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.DISABLED)
                self.update_status("Iniciando serviços...")
                self.log("Executando 'docker compose up -d'...")

                process = subprocess.Popen(
                    ["docker", "compose", "up", "-d"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=self.install_dir,
                    encoding="utf-8",
                    errors="replace",
                )

                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    self.log(line.strip())
                
                process.wait()

                if process.returncode == 0:
                    self.log("Serviços iniciados com sucesso!")
                    self.update_status("Serviços em execução")
                    self.is_running = True

                    self.stop_btn.config(state=tk.NORMAL)
                    self.open_app_btn.config(state=tk.NORMAL)
                    self.whatsapp_btn.config(state=tk.NORMAL)

                    self.connect_to_redis()
                    time.sleep(5)
                    self.check_services_status()
                else:
                    self.log(f"Erro ao iniciar serviços (código: {process.returncode}).")
                    self.update_status("Erro ao iniciar")
                    messagebox.showerror(
                        "Erro", "Ocorreu um erro ao iniciar os serviços. Verifique o log."
                    )
            except Exception as e:
                self.log(f"Erro ao iniciar serviços: {e!s}")
                self.update_status("Erro ao iniciar")
                messagebox.showerror("Erro", f"Erro ao iniciar serviços: {e!s}")
            finally:
                self.start_btn.config(state=tk.NORMAL)

        threading.Thread(target=run_start, daemon=True).start()

    def stop_services(self, from_rebuild=False):
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
                    self.open_app_btn.config(state=tk.DISABLED)
                    self.whatsapp_btn.config(state=tk.DISABLED)

                else:
                    self.log(f"Erro ao parar serviços: {result.stderr}")
                    self.update_status("Erro ao parar")
                    if not from_rebuild:
                        messagebox.showerror("Erro", f"Erro ao parar serviços: {result.stderr}")

            except Exception as e:
                self.log(f"Erro ao parar serviços: {e!s}")
                self.update_status("Erro ao parar")
                if not from_rebuild:
                    messagebox.showerror("Erro", f"Erro ao parar serviços: {e!s}")
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
                encoding="utf-8",
            )

            if result.returncode == 0 and result.stdout.strip():
                services = []
                for line in result.stdout.strip().split("\n"):
                    if not line.strip(): continue
                    try:
                        parsed_line = json.loads(line)
                        if isinstance(parsed_line, list):
                            services.extend(parsed_line)
                        elif isinstance(parsed_line, dict):
                            services.append(parsed_line)
                    except json.JSONDecodeError:
                        self.log(f"Aviso: Não foi possível decodificar a linha JSON: {line}")

                if not services:
                    self.log("Nenhum serviço Docker encontrado.")
                    return

                running_services = [s for s in services if s.get("State") == "running"]
                self.log(f"Serviços em execução: {len(running_services)}/{len(services)}")
                for service in services:
                    name = service.get("Service", service.get("Name", "unknown"))
                    state = service.get("State", "unknown")
                    self.log(f"  - {name}: {state}")

        except Exception as e:
            self.log(f"Erro ao verificar status dos serviços: {e!s}")

    def open_interface(self):
        """Abre a interface web do Streamlit"""
        url = "http://localhost:8501"
        self.log(f"Abrindo a aplicação: {url}")
        webbrowser.open(url)

    def open_whatsapp_config(self):
        """Abre a página de configuração do WhatsApp no app"""
        url = "http://localhost:3000/dashboard"
        self.log(f"Abrindo configurações do WhatsApp: {url}")
        webbrowser.open(url)

    def uninstall(self):
        """Desinstala a aplicação"""
        if messagebox.askyesno(
            "Confirmar Desinstalação", "Tem certeza que deseja desinstalar o Repense Assistente?\n\nTodos os dados, incluindo configurações e imagens, serão permanentemente removidos."
        ):
            try:
                if self.is_running:
                    self.stop_services()
                    time.sleep(3)

                self.log("Removendo containers, imagens e volumes Docker...")
                subprocess.run(
                    ["docker", "compose", "down", "--rmi", "all", "--volumes"],
                    cwd=self.install_dir,
                    capture_output=True,
                )

                if self.install_dir.exists():
                    self.log("Removendo diretório de instalação...")
                    shutil.rmtree(self.install_dir)

                self.log("Desinstalação concluída!")
                messagebox.showinfo("Sucesso", "Repense Assistente foi desinstalado.")
                self.root.quit()

            except Exception as e:
                self.log(f"Erro durante desinstalação: {e!s}")
                messagebox.showerror("Erro", f"Erro durante desinstalação: {e!s}")

    def check_initial_status(self):
        """Verifica o status inicial da aplicação"""
        config = self.load_config()

        if config and self.install_dir.exists():
            self.log("Instalação existente encontrada.")
            self.update_status("Instalado")
            self.start_btn.config(state=tk.NORMAL)
            self.uninstall_btn.config(state=tk.NORMAL)
            try:
                result = subprocess.run(
                    ["docker", "compose", "ps", "-q"],
                    capture_output=True,
                    text=True,
                    cwd=self.install_dir,
                )
                if result.returncode == 0 and result.stdout.strip():
                    self.log("Serviços detectados como em execução.")
                    self.update_status("Serviços em execução")
                    self.is_running = True
                    self.stop_btn.config(state=tk.NORMAL)
                    self.open_app_btn.config(state=tk.NORMAL)
                    self.whatsapp_btn.config(state=tk.NORMAL)
                    self.check_services_status()
                    self.connect_to_redis()
            except:
                pass
        else:
            self.log("Nenhuma instalação encontrada.")
            self.update_status("Não instalado")

    def run(self):
        """Executa o instalador"""
        self.setup_gui()
        self.log(f"Iniciando {self.app_name} Installer v{self.version}")
        self.root.mainloop()


if __name__ == "__main__":
    installer = RepensenAssistenteInstaller()
    installer.run()
