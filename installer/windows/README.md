# Instalador Windows - Repense Assistente

Este diretório contém o instalador para Windows do Repense Assistente, que permite instalar, atualizar e gerenciar containers Docker automaticamente.

## Características

- ✅ **Interface Gráfica Intuitiva**: Interface amigável com Tkinter
- ✅ **Verificação Automática de Atualizações**: Verifica atualizações no GitHub automaticamente
- ✅ **Gerenciamento de Containers Docker**: Inicia, para e monitora containers automaticamente
- ✅ **Instalação Automática**: Baixa e instala o projeto automaticamente
- ✅ **Configuração Automática**: Cria arquivos de configuração necessários
- ✅ **Verificação de Dependências**: Verifica se Docker está instalado
- ✅ **Desinstalação Completa**: Remove todos os arquivos e containers

## Pré-requisitos

### Para Usar o Instalador
- Windows 10/11
- Docker Desktop instalado
- Conexão com a internet

### Para Compilar o Instalador
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- PyInstaller
- Conexão com a internet

## Como Usar

### 1. Executar o Instalador Pré-compilado

1. Baixe o arquivo `RepensenAssistente-Installer.exe`
2. Execute o arquivo como administrador (recomendado)
3. Siga as instruções na interface gráfica:
   - Clique em "Instalar/Atualizar" para baixar e instalar
   - Configure o arquivo `.env` com suas chaves de API
   - Clique em "Iniciar Serviços" para rodar os containers
   - Clique em "Abrir Interface" para acessar o Streamlit

### 2. Funcionalidades do Instalador

#### Instalação/Atualização
- Verifica se Docker está instalado
- Baixa a versão mais recente do GitHub
- Extrai arquivos para `%USERPROFILE%\RepensenAssistente`
- Cria arquivo `.env` com configurações padrão
- Salva configurações de instalação

#### Gerenciamento de Serviços
- **Iniciar Serviços**: Executa `docker compose up -d`
- **Parar Serviços**: Executa `docker compose down`
- **Verificar Status**: Mostra status de cada container
- **Abrir Interface**: Abre http://localhost:8501 no navegador

#### Verificação de Atualizações
- Verifica automaticamente no GitHub
- Notifica quando há novas versões
- Permite atualização com um clique

#### Desinstalação
- Para todos os serviços
- Remove containers e imagens Docker
- Remove diretório de instalação
- Limpa configurações

## Como Compilar

### Método 1: Usando o Script Batch (Recomendado)

1. Abra o Prompt de Comando como administrador
2. Navegue até o diretório `installer/windows`
3. Execute:
   ```cmd
   build.bat
   ```

### Método 2: Usando Python Diretamente

1. Instale as dependências:
   ```cmd
   pip install pyinstaller requests pathlib
   ```

2. Compile o instalador:
   ```cmd
   pyinstaller installer.spec
   ```

3. O executável será criado em `dist/RepensenAssistente-Installer.exe`

### Método 3: Usando o Script Python

```cmd
python build.py
```

## Estrutura de Arquivos

```
installer/windows/
├── installer.py          # Script principal do instalador
├── updater.py           # Sistema de atualizações automáticas
├── build.py             # Script para compilar o instalador
├── build.bat            # Script batch para Windows
├── installer.spec       # Configuração do PyInstaller
├── version_info.txt     # Informações de versão do executável
├── icon.ico            # Ícone do instalador (opcional)
├── README.md           # Esta documentação
└── dist/               # Diretório com executável compilado
    └── RepensenAssistente-Installer.exe
```

## Configuração

### Arquivo .env

O instalador cria automaticamente um arquivo `.env` com as seguintes configurações:

```env
# Configurações do Repense Assistente
OPENAI_API_KEY=your_openai_api_key_here
REDIS_URL=redis://redis:6379

# Configurações do WAHA
WAHA_PRINT_QR=false
TZ=America/Sao_Paulo

# Configurações do ambiente
ENVIRONMENT=production
```

**Importante**: Configure sua chave da OpenAI antes de iniciar os serviços.

### Configurações do Atualizador

O sistema de atualizações pode ser configurado através da interface gráfica ou editando o arquivo `%USERPROFILE%\RepensenAssistente\updater_config.json`:

```json
{
  "auto_check": true,
  "notify_updates": true,
  "auto_download": false,
  "current_version": "1.0.0",
  "last_check": "2024-01-01T12:00:00"
}
```

## Personalização

### Alterar Repositório GitHub

Para usar seu próprio repositório, edite as seguintes linhas em `installer.py`:

```python
self.github_repo = "seu-usuario/repense-assistente"  # Linha 22
```

E em `updater.py`:

```python
self.github_repo = "seu-usuario/repense-assistente"  # Linha 16
```

### Adicionar Ícone Personalizado

1. Coloque um arquivo `icon.ico` no diretório `installer/windows/`
2. O ícone será automaticamente incluído no executável

### Modificar Informações de Versão

Edite o arquivo `version_info.txt` para alterar as informações exibidas no executável.

## Solução de Problemas

### Docker não encontrado
- Instale o Docker Desktop do site oficial
- Reinicie o computador após a instalação
- Verifique se o Docker está rodando na bandeja do sistema

### Erro de permissões
- Execute o instalador como administrador
- Verifique se o antivírus não está bloqueando

### Erro de rede
- Verifique sua conexão com a internet
- Verifique se o firewall não está bloqueando
- Tente usar uma VPN se houver restrições

### Containers não iniciam
- Verifique se as portas 3000, 6380, 8000 e 8501 estão livres
- Verifique os logs com `docker compose logs`
- Reinicie o Docker Desktop

### Erro na compilação
- Verifique se o Python está instalado corretamente
- Instale as dependências manualmente:
  ```cmd
  pip install pyinstaller requests pathlib tkinter
  ```
- Tente compilar em modo verbose:
  ```cmd
  pyinstaller --log-level DEBUG installer.spec
  ```

## Logs e Debugging

### Logs do Instalador
Os logs são exibidos na interface gráfica e também no console se executado via linha de comando.

### Logs dos Containers
Para ver logs dos containers:
```cmd
cd %USERPROFILE%\RepensenAssistente
docker compose logs
```

### Logs específicos de um serviço:
```cmd
docker compose logs fastapi
docker compose logs streamlit
docker compose logs waha
docker compose logs redis
```

## Distribuição

### Criar Pacote de Distribuição

1. Compile o instalador
2. Teste em uma máquina limpa
3. Crie um arquivo ZIP com:
   - `RepensenAssistente-Installer.exe`
   - `README.md` (instruções para usuário final)
   - `LICENSE` (se aplicável)

### Upload para GitHub Releases

1. Crie uma nova release no GitHub
2. Faça upload do executável
3. Adicione notas de versão
4. Marque como "Latest release"

## Segurança

### Considerações de Segurança

- O instalador baixa código do GitHub - certifique-se de que o repositório é confiável
- Execute sempre como administrador para evitar problemas de permissão
- Mantenha o Docker Desktop atualizado
- Configure adequadamente as chaves de API no arquivo `.env`

### Antivírus

Alguns antivírus podem detectar o executável como suspeito devido ao PyInstaller. Para resolver:

1. Adicione exceção no antivírus
2. Assine digitalmente o executável (para distribuição comercial)
3. Use certificados de código válidos

## Contribuição

Para contribuir com melhorias no instalador:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Teste thoroughly em diferentes versões do Windows
4. Submeta um Pull Request

## Licença

Este instalador segue a mesma licença do projeto principal Repense Assistente.

## Suporte

Para suporte técnico:
- Abra uma issue no GitHub
- Inclua logs relevantes
- Descreva o ambiente (versão do Windows, Docker, etc.)
- Inclua passos para reproduzir o problema
