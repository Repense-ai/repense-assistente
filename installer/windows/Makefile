# Makefile para o Instalador Windows do Repense Assistente

.PHONY: help install-deps build clean test package all

PYTHON = python
PIP = pip
PYINSTALLER = pyinstaller
INSTALLER_NAME = repense-assistente
DIST_DIR = dist
BUILD_DIR = build

help:
	@echo "Makefile para o Instalador Windows do Repense Assistente"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  help         - Mostra esta ajuda"
	@echo "  install-deps - Instala dependências necessárias"
	@echo "  build        - Compila o instalador"
	@echo "  clean        - Remove arquivos de build"
	@echo "  test         - Testa o instalador compilado"
	@echo "  package      - Cria pacote para distribuição"
	@echo "  all          - Executa install-deps, clean, build e package"

install-deps:
	@echo "Instalando dependências..."
	$(PIP) install -r requirements.txt
	@echo "Dependências instaladas com sucesso!"

build:
	@echo "Compilando instalador..."
	$(PYINSTALLER) installer.spec
	@echo "Instalador compilado com sucesso!"

clean:
	@echo "Limpando arquivos de build..."
	@if exist "$(BUILD_DIR)" rmdir /s /q "$(BUILD_DIR)"
	@if exist "$(DIST_DIR)" rmdir /s /q "$(DIST_DIR)"
	@echo "Limpeza concluída!"

test:
	@echo "Testando instalador..."
	@if exist "$(DIST_DIR)\$(INSTALLER_NAME).exe" ( \
		echo "Instalador encontrado!" \
	) else ( \
		echo "ERRO: Instalador não encontrado!" \
	)

package:
	@echo "Criando pacote para distribuição..."
	@if not exist "release" mkdir release
	@copy "$(DIST_DIR)\$(INSTALLER_NAME).exe" "release\" 2>nul || echo "Erro ao copiar instalador"
	@copy "README.md" "release\" 2>nul || echo "Erro ao copiar README"
	@echo "Pacote criado em: release\"

all: install-deps clean build package
	@echo "Build completo concluído!"

check-env:
	@echo "Verificando ambiente..."
	@$(PYTHON) --version
	@$(PIP) --version
	@$(PYINSTALLER) --version
