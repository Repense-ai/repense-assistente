# Repense Assistente - Instalador Windows

## Instruções Rápidas

### 1. Pré-requisitos
- Windows 10 ou 11
- Docker Desktop instalado ([Download aqui](https://www.docker.com/products/docker-desktop/))
- Conexão com a internet

### 2. Como Instalar

1. **Execute o instalador**
   - Baixe `RepensenAssistente-Installer.exe`
   - Execute como administrador (clique com botão direito → "Executar como administrador")

2. **Siga os passos na interface**
   - Clique em "Instalar/Atualizar"
   - Aguarde o download e instalação
   - Configure suas chaves de API no arquivo `.env`

3. **Inicie os serviços**
   - Clique em "Iniciar Serviços"
   - Aguarde os containers iniciarem
   - Clique em "Abrir Interface" para acessar o sistema

### 3. Configuração Inicial

Após a instalação, você precisa configurar suas chaves de API:

1. Navegue até `%USERPROFILE%\RepensenAssistente`
2. Abra o arquivo `.env` em um editor de texto
3. Substitua `your_openai_api_key_here` pela sua chave da OpenAI
4. Salve o arquivo
5. Reinicie os serviços no instalador

### 4. Acessando o Sistema

- **Interface Principal**: http://localhost:8501
- **API**: http://localhost:8000
- **WhatsApp (WAHA)**: http://localhost:3000

### 5. Solução de Problemas

#### Docker não encontrado
- Instale o Docker Desktop
- Reinicie o computador
- Verifique se o Docker está rodando (ícone na bandeja)

#### Erro de permissões
- Execute o instalador como administrador
- Desative temporariamente o antivírus

#### Serviços não iniciam
- Verifique se as portas não estão em uso
- Reinicie o Docker Desktop
- Verifique os logs no instalador

#### Erro de rede
- Verifique sua conexão com a internet
- Verifique configurações de firewall
- Tente usar uma VPN se necessário

### 6. Atualizações

O instalador verifica automaticamente por atualizações. Quando uma nova versão estiver disponível:

1. Uma notificação aparecerá
2. Clique em "Sim" para baixar
3. Execute o novo instalador
4. Ele detectará e atualizará a instalação existente

### 7. Desinstalação

Para remover completamente o Repense Assistente:

1. Abra o instalador
2. Clique em "Desinstalar"
3. Confirme a remoção
4. Todos os arquivos e containers serão removidos

### 8. Suporte

- **GitHub**: [Repositório do projeto]
- **Issues**: [Link para issues]
- **Documentação**: [Link para docs]

---

**Importante**: Mantenha suas chaves de API seguras e nunca as compartilhe publicamente.
