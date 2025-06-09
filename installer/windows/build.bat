@echo off
echo ===================================
echo  Build do Instalador Windows
echo  Repense Assistente
echo ===================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado!
    echo Instale o Python 3.8+ antes de continuar.
    pause
    exit /b 1
)

echo Python encontrado!
echo.

REM Instalar dependências
echo Instalando dependências...
pip install pyinstaller requests pathlib

if errorlevel 1 (
    echo ERRO: Falha ao instalar dependências!
    pause
    exit /b 1
)

echo.
echo Compilando instalador...

REM Compilar usando PyInstaller
pyinstaller installer.spec

if errorlevel 1 (
    echo ERRO: Falha na compilação!
    pause
    exit /b 1
)

echo.
echo ===================================
echo  Build concluído com sucesso!
echo ===================================
echo.
echo O instalador foi criado em: dist\RepensenAssistente-Installer.exe
echo.

REM Verificar se o arquivo foi criado
if exist "dist\RepensenAssistente-Installer.exe" (
    echo Arquivo criado com sucesso!
    echo Tamanho:
    dir "dist\RepensenAssistente-Installer.exe" | find "RepensenAssistente-Installer.exe"
) else (
    echo AVISO: Arquivo executável não encontrado!
)

echo.
echo Pressione qualquer tecla para continuar...
pause >nul
