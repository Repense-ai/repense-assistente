"""
Chatbot interface using Streamlit's chat components and Redis for memory management.
"""

import os
from datetime import datetime

import redis
import streamlit as st
from openai import OpenAI

from app.prompts.atendimento import PROMPT_ASSISTENTE
from src.memory import RedisManager

# Page configuration
st.set_page_config(
    page_title="Repense.ai - Assistente",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Redis client
try:
    redis_client = redis.Redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True
    )
    redis_client.ping()  # Check connection
except redis.exceptions.ConnectionError as e:
    st.error(f"Não foi possível conectar ao Redis. Verifique se os serviços estão rodando. Detalhes: {e}")
    st.stop()

# Initialize OpenAI client
config_manager = RedisManager(redis_client, "config")
# Safely get config, default to an empty dict if it doesn't exist
config = config_manager.get_memory_dict() or {} 
api_key = config.get("OPENAI_API_KEY")

if not api_key:
    st.warning("⚠️ A chave de API da OpenAI não foi configurada.")
    st.info("Por favor, vá para a página de configurações para adicionar sua chave.")
    if st.button("Ir para Configurações"):
        st.switch_page("pages/Configurações.py")
    st.stop()

try:
    client = OpenAI(api_key=api_key)
    # Test the key with a lightweight call
    client.models.list()
except Exception as e:
    st.error(f"A chave de API configurada é inválida ou expirou. Por favor, atualize-a na página de configurações. Erro: {e}")
    if st.button("Ir para Configurações"):
        st.switch_page("pages/Configurações.py")
    st.stop()

# Initialize Redis manager for persistent chat history
chat_manager = RedisManager(redis_client, "chat_history")
stored_messages = chat_manager.get_memory_dict()

# Provide defaults for prompt formatting to avoid errors if config is partial
prompt_defaults = {
    "business_name": "a empresa",
    "business_description": "Não há descrição do negócio.",
    "assistant_name": "Assistente",
    "tone": "profissional",
    "use_emojis": "Não",
    "instructions": "Nenhuma instrução adicional.",
}
# Merge defaults with actual config
prompt_config = {**prompt_defaults, **config}

# Initialize session state for chat history
if "messages" not in st.session_state:
    # Load from Redis if available, otherwise start fresh
    if stored_messages and "messages" in stored_messages:
        st.session_state.messages = stored_messages["messages"]
    else:
        st.session_state.messages = [
            {"role": "system", "content": PROMPT_ASSISTENTE.format(**prompt_config)},
        ]

# Chat interface header
st.header("💬 Assistente Virtual")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "system":
        with st.expander("Instruções do Assistente", expanded=False):
            st.write(message["content"])
            continue
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Digite sua mensagem..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Display assistant response with loading spinner
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Get assistant response
        try:
            # Create the messages list for the API call
            messages_for_api = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

            # Make API call
            response = client.chat.completions.create(
                model="gpt-4.1",  # Recommended model
                messages=messages_for_api,
                stream=True,
                temperature=0.7,
            )

            # Stream the response
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.write(full_response + "▌")

            # Update final response
            message_placeholder.write(full_response)

            # Add assistant response to chat history
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

            # Save updated chat history to Redis
            chat_manager.set_memory_dict(
                {
                    "messages": st.session_state.messages,
                    "last_updated": datetime.now().isoformat(),
                }
            )

        except Exception as e:
            st.error(f"Ocorreu um erro ao comunicar com a OpenAI: {e}")

# Sidebar with chat controls
with st.sidebar:
    st.title("Configurações do Chat")

    # Clear chat history button
    if st.button("🗑️ Limpar"):
        st.session_state.messages = []
        chat_manager.reset_memory_dict()
        st.rerun()

    # Download chat history
    if st.session_state.messages:
        chat_text = "\n\n".join(
            [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages if m['role'] != 'system']
        )

        st.download_button(
            "📥 Baixar",
            chat_text,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
        )
