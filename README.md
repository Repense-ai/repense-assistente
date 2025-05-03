# Repense Assistente

Seu assistente do dia a dia. Seja no comércio ou pessoal, o assistente pode te ajudar com tarefas cotidianas.

## Sobre o Projeto

O Repense Assistente é uma aplicação que integra WhatsApp com inteligência artificial para criar um assistente virtual para negócios e uso pessoal. A aplicação utiliza o serviço WAHA para integração com WhatsApp, Redis para armazenamento de dados, FastAPI para o backend e Streamlit para a interface de usuário.

## Arquitetura

O projeto é composto por vários serviços que trabalham juntos:

- **WAHA**: Serviço para integração com WhatsApp
- **Redis**: Banco de dados em memória para armazenamento de mensagens e configurações
- **FastAPI**: API REST para processamento de webhooks e gerenciamento de dados
- **Streamlit**: Interface de usuário para configuração e monitoramento

## Tecnologias Utilizadas

- **Python 3.12+**: Linguagem de programação principal
- **FastAPI**: Framework para desenvolvimento de APIs
- **Streamlit**: Framework para desenvolvimento de interfaces de usuário
- **Redis**: Banco de dados em memória
- **Docker**: Containerização de aplicações
- **ChromaDB**: Banco de dados vetorial para armazenamento de embeddings
- **RepenseAI**: SDK para integração com modelos de IA

## Pré-requisitos

- Python 3.12 ou superior
- Docker e Docker Compose
- Chave de API para serviços de IA (OpenAI, etc.)

## Instalação

### Usando Docker (Recomendado)

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/repense-assistente.git
   cd repense-assistente
   ```

2. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas chaves de API
   ```

3. Inicie os serviços com Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Acesse a interface web em `http://localhost:8501`

### Instalação Local

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/repense-assistente.git
   cd repense-assistente
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install uv
   uv sync
   ```

4. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas chaves de API
   ```

5. Inicie o Redis localmente ou use um serviço externo

6. Inicie a API:
   ```bash
   uv run ./api/main.py
   ```

7. Em outro terminal, inicie a interface web:
   ```bash
   uv run streamlit run ./app/home.py
   ```

## Desenvolvimento

### Configuração do Ambiente de Desenvolvimento

1. Instale as dependências de desenvolvimento:
   ```bash
   uv sync --dev
   ```

2. Configure o pre-commit:
   ```bash
   pre-commit install
   ```

### Linting e Formatação

O projeto utiliza várias ferramentas para garantir a qualidade do código:

```bash
make lint  # Executa black, isort, ruff, autoflake e flake8
```

ou

```bash
make pre-commit  # Executa todas as verificações do pre-commit
```

## Uso

### Configuração do Webhook

O serviço `webhook-config` configura automaticamente o webhook do WAHA para enviar mensagens para a API FastAPI. Você pode verificar a configuração acessando `http://localhost:3000` (interface do WAHA).

### Interface Web

Acesse a interface web em `http://localhost:8501` para configurar e monitorar o assistente.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
