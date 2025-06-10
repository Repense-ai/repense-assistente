"""
Test page for Redis volume functionality.

This module provides a UI for testing Redis configuration and persistence.
"""

import os
from datetime import datetime

import openai
import redis
import streamlit as st

from src.memory import RedisManager

# --- Utility Functions ---

def show_notification(message, type='info'):
    """Displays a notification message in the UI."""
    if type == 'success':
        st.success(message)
    elif type == 'warning':
        st.warning(message)
    elif type == 'error':
        st.error(message)
    else:
        st.info(message)

def validate_api_key(api_key: str) -> bool:
    """Validates the OpenAI API key."""
    if not api_key or not api_key.strip():
        return False
    try:
        client = openai.OpenAI(api_key=api_key.strip())
        client.models.list()
        return True
    except Exception:
        return False

# --- Initialization ---

st.set_page_config(page_title="Repense.ai - Configurações", page_icon="⚙️", layout="wide")

try:
    redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)
    config_manager = RedisManager(redis_client, "config")
    openai_api_key_manager = RedisManager(redis_client, "secrets:openai_api_key")
except redis.exceptions.ConnectionError as e:
    st.error(f"Não foi possível conectar ao Redis. Verifique se os serviços estão rodando. Detalhes: {e}")
    st.stop()

# Load existing data
current_config = config_manager.get_memory_dict()
api_key_persisted = openai_api_key_manager.get_memory_dict().get('key')

# --- UI Rendering ---

st.title("Configurações Gerais")
st.write("Gerencie as configurações do seu assistente virtual e da API da OpenAI.")

# --- OpenAI API Key Management ---
st.header("Chave da API OpenAI")
notification_placeholder = st.empty()

with st.container():
    api_key_input = st.text_input(
        "Insira sua chave da API da OpenAI",
        type="password",
        placeholder="sk-...",
        help="Sua chave é armazenada de forma segura e não é compartilhada."
    )

    if st.button("Salvar/Atualizar Chave da OpenAI"):
        if validate_api_key(api_key_input):
            key = api_key_input.strip()
            openai_api_key_manager.set_memory_dict({'key': key})
            with notification_placeholder.container():
                show_notification("✅ Chave da API da OpenAI salva com sucesso!", 'success')
            st.rerun()
        else:
            with notification_placeholder.container():
                show_notification("❌ Chave da API inválida. Verifique e tente novamente.", 'error')

if not api_key_persisted:
    with notification_placeholder.container():
        show_notification(
            "⚠️ A chave da API da OpenAI não está configurada.",
            'warning'
        )
else:
    with notification_placeholder.container():
        show_notification(
            "✅ A chave da API da OpenAI está configurada.",
            'success'
        )

st.divider()

# --- Assistant Configuration ---
st.header("Configuração do Assistente")

with st.form("assistant_config_form"):
    st.subheader("Informações do Negócio")
    business_name = st.text_input("Nome da Empresa", value=current_config.get("business_name", ""))
    business_description = st.text_area("Descrição do Negócio", value=current_config.get("business_description", ""), height=100)
    business_segment = st.selectbox(
        "Segmento",
        ["Varejo", "Serviços", "Tecnologia", "Saúde", "Educação", "Outro"],
        index=["Varejo", "Serviços", "Tecnologia", "Saúde", "Educação", "Outro"].index(current_config.get("business_segment", "Varejo"))
    )

    st.subheader("Personalidade do Assistente")
    assistant_name = st.text_input("Nome do Assistente", value=current_config.get("assistant_name", ""))
    tone = st.select_slider(
        "Tom de Voz",
        options=["profissional", "amigável", "casual", "entusiasmado"],
        value=current_config.get("tone", "profissional")
    )
    use_emojis = st.toggle("Usar Emojis", value=current_config.get("use_emojis", True))
    instructions = st.text_area("Instruções Adicionais", value=current_config.get("instructions", ""), height=100)

    submit_button = st.form_submit_button("Salvar Configurações do Assistente", use_container_width=True)

    if submit_button:
        if not api_key_persisted:
            show_notification("❌ Por favor, salve uma chave da API da OpenAI válida antes de salvar as configurações.", 'error')
        else:
            config_data = {
                "business_name": business_name,
                "business_description": business_description,
                "business_segment": business_segment,
                "assistant_name": assistant_name,
                "tone": tone,
                "use_emojis": use_emojis,
                "instructions": instructions,
                "last_updated": datetime.now().isoformat(),
            }
            try:
                config_manager.set_memory_dict(config_data)
                show_notification("✅ Configurações do assistente salvas com sucesso!", 'success')
            except Exception as e:
                show_notification(f"❌ Erro ao salvar as configurações: {e}", 'error')

st.divider()

# --- Actions ---
st.header("Ações")
col1, col2 = st.columns(2)

with col1:
    if st.button("Ir para o Assistente", use_container_width=True, type="primary"):
        st.switch_page("pages/Assistente.py")

with col2:
    if st.button("Configurar WhatsApp", use_container_width=True):
        st.info("Esta funcionalidade ainda não foi implementada.") # Placeholder
