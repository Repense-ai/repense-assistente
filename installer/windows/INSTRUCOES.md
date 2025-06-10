# Repense Assistente - Instalador Windows

Este documento contém instruções para **usuários finais** e **desenvolvedores**.

---

## 1. Instruções para Usuários Finais

### Pré-requisitos
- Windows 10 ou 11.
- **Docker Desktop**: É essencial que o Docker Desktop esteja instalado e em execução. [Faça o download aqui](https://www.docker.com/products/docker-desktop/).
- Conexão com a internet.

### Como Instalar e Configurar
1.  **Execute o Instalador**: Baixe o `RepensenAssistente-Installer.exe` e execute-o como **administrador** (clique com o botão direito -> "Executar como administrador").
2.  **Instale os Serviços**: Na tela do instalador, clique em "Instalar/Atualizar". O programa fará o download dos arquivos necessários para a pasta `%USERPROFILE%\RepensenAssistente`.
3.  **Inicie os Serviços**: Após a instalação, clique em "Iniciar Serviços". Aguarde até que os containers do Docker sejam iniciados e o status mude para "Serviços em execução".
4.  **Configure a Chave de API**:
    - Com os serviços em execução, clique no botão **"Configurar"**.
    - Uma janela aparecerá solicitando sua **OpenAI API Key**.
    - Insira sua chave e clique em "OK". Ela será salva de forma segura.
5.  **Acesse a Interface**: Após configurar a chave, clique em "Abrir Interface" para acessar o sistema no seu navegador.

### Acessos
- **Interface Principal**: http://localhost:8501
- **API**: http://localhost:8000
- **WhatsApp (WAHA)**: http://localhost:3000

### Solução de Problemas
- **Docker não encontrado**: Certifique-se de que o Docker Desktop está instalado e rodando. O ícone da baleia deve aparecer na bandeja do sistema.
- **Erro de permissões**: Sempre execute o instalador como administrador.
- **Serviços não iniciam**: Verifique se as portas (`8501`, `8000`, `3000`) não estão sendo usadas por outros programas. Tente reiniciar o Docker Desktop.
- **Erro ao Configurar**: Se a configuração da chave de API falhar, verifique se os serviços (especialmente o Redis) estão rodando corretamente. Você pode usar o comando `docker ps` no terminal para verificar.

---

## 2. Instruções para Desenvolvedores

### Ambiente de Desenvolvimento
- **Python 3.8+**
- **Git**
- **Docker Desktop**

### Como Compilar o Instalador (Build)

O processo de compilação é automatizado por scripts.

1.  **Clone o Repositório**:
    ```bash
    git clone https://github.com/Repense-ai/repense-assistente.git
    cd repense-assistente/installer/windows
    ```

2.  **Execute o Script de Build**:
    Abra o terminal (CMD ou PowerShell) e execute o `build.bat`:
    ```bash
    .\build.bat
    ```
    O script irá:
    - Criar um ambiente virtual (`.venv`).
    - Instalar as dependências do `requirements.txt` (incluindo `pyinstaller` e `redis`).
    - Executar o PyInstaller para empacotar a aplicação em um único `.exe`.

3.  **Encontre o Instalador**:
    O instalador final, `RepensenAssistente-Installer.exe`, estará na pasta `installer/windows/dist`.

### Como Testar o Instalador

É crucial testar o instalador em um ambiente limpo para simular a experiência do usuário.

**Ambiente de Teste Recomendado:**
- Uma máquina virtual Windows (usando VirtualBox, VMware, ou Hyper-V).
- Uma instalação limpa do Windows 10 ou 11, sem ferramentas de desenvolvimento.

**Passos para o Teste:**

1.  **Preparação do Ambiente Limpo**:
    - Na sua máquina virtual, instale o **Docker Desktop**.
    - Certifique-se de que não há nenhuma instalação anterior do Repense Assistente.

2.  **Teste de Instalação**:
    - Copie o `RepensenAssistente-Installer.exe` para a máquina virtual.
    - Execute-o **como administrador**.
    - Clique em "Instalar/Atualizar" e aguarde a conclusão.

3.  **Teste de Configuração e Execução**:
    - Clique em "Iniciar Serviços". Aguarde a inicialização.
    - Clique em "Configurar" e insira uma chave de API da OpenAI válida.
    - **Verifique**:
        - Os logs indicam que os containers estão rodando.
        - O botão "Abrir Interface" está habilitado.
        - Uma mensagem confirma que a chave foi salva.

4.  **Teste de Funcionalidade**:
    - Clique em "Abrir Interface" e verifique se a aplicação web (`http://localhost:8501`) funciona e responde corretamente, utilizando a chave de API configurada.

5.  **Teste de Parada e Desinstalação**:
    - No instalador, clique em "Parar Serviços" e verifique se os containers param (com `docker ps`).
    - Clique em "Desinstalar" e confirme que a pasta `%USERPROFILE%\RepensenAssistente` é removida.
        
### Importante
- A aplicação principal (dentro do Docker) deve ser adaptada para ler a `OPENAI_API_KEY` do Redis, em vez de um arquivo `.env`.
- Mantenha suas chaves de API seguras.
