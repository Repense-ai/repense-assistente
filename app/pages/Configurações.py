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

# Functions


def validate_api_key(api_key: str) -> bool:
    """
    Validate if the provided API key is valid.

    Args:
        api_key (str): The OpenAI API key to validate

    Returns:
        bool: True if key is valid, False otherwise
    """
    if not api_key:
        return False
    try:
        api_key = api_key.strip()
        client = openai.OpenAI(api_key=api_key)
        # Make a simple API call to test the key
        _ = client.models.list()
        return True
    except Exception as e:
        st.error(f"API key validation failed: {e!s}")
        return False


# Initialize Redis client
redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True
)

# Initialize config manager
config_manager = RedisManager(redis_client, "config")

# Load existing configuration
current_config = config_manager.get_memory_dict() or {}
if "validated_api_key" not in st.session_state:
    st.session_state.validated_api_key = None

# Configure page
st.set_page_config(
    page_title="Repense.ai - Assistente", page_icon="🤖", layout="centered"
)

# API Key Management
st.header("Configuração da API OpenAI")

existing_key = current_config.get("OPENAI_API_KEY")

if existing_key:
    st.success("✅ API Key da OpenAI já está configurada!")
else:
    st.warning(
        "⚠️ API Key da OpenAI não está configurada. Por favor, configure-a abaixo."
    )

api_key_input = st.text_input(
    "Digite sua API Key da OpenAI para validar ou atualizar",
    type="password",
    help="Você pode obter sua API key em: https://platform.openai.com/api-keys",
)

if st.button("Validar e Salvar Chave Temporariamente"):
    if validate_api_key(api_key_input):
        st.session_state.validated_api_key = api_key_input
        st.success("✅ API Key validada e pronta para ser salva com as configurações.")
    else:
        st.error("❌ API Key inválida. Por favor, verifique e tente novamente.")

st.divider()

st.title("Configuração do Assistente Virtual")

with st.form("assistant_config"):
    # Informações do Negócio
    st.subheader("Informações do Negócio")
    business_name = st.text_input(
        "Nome da Empresa",
        value=current_config.get("business_name", ""),
        help="Nome da sua empresa",
    )

    business_description = st.text_area(
        "Descrição do Negócio",
        value=current_config.get("business_description", ""),
        help="Descreva brevemente o que sua empresa faz",
        height=100,
    )

    business_segment = st.selectbox(
        "Segmento",
        options=["Varejo", "Serviços", "Tecnologia", "Saúde", "Educação", "Outro"],
        index=["Varejo", "Serviços", "Tecnologia", "Saúde", "Educação", "Outro"].index(
            current_config.get("business_segment", "Varejo")
        ),
    )

    # Configuração da Personalidade do Assistente
    st.subheader("Personalidade do Assistente")

    assistant_name = st.text_input(
        "Nome do Assistente",
        value=current_config.get("assistant_name", ""),
        help="Como seu assistente virtual deve se apresentar",
    )

    tone_options = {
        "profissional": "Profissional e Formal",
        "amigável": "Amigável e Informal",
        "casual": "Casual e Descontraído",
        "entusiasmado": "Entusiasmado e Energético",
    }

    tone = st.select_slider(
        "Tom de Voz",
        options=list(tone_options.keys()),
        value=current_config.get("tone", "profissional"),
        format_func=lambda x: tone_options[x],
    )

    use_emojis = st.toggle(
        "Usar Emojis nas Respostas",
        value=current_config.get("use_emojis", True),
        help="Permite que o assistente use emojis em suas respostas",
    )

    instructions = st.text_area(
        "Instruções Adicionais",
        value=current_config.get("instructions", ""),
        help="Instruções adicionais para o assistente",
        height=100,
    )

    # Botão de Salvar
    submitted = st.form_submit_button("Salvar Configurações")

    if submitted:
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

        # Use the newly validated key from session state, or fall back to existing key
        if st.session_state.validated_api_key:
            config_data["OPENAI_API_KEY"] = st.session_state.validated_api_key
        elif existing_key:
            config_data["OPENAI_API_KEY"] = existing_key
        else:
            st.error(
                "Nenhuma chave API da OpenAI foi configurada. Valide uma chave antes de salvar."
            )
            st.stop()

        try:
            config_manager.set_memory_dict(config_data)
            st.success("✅ Configurações salvas com sucesso!")
            # Clear the temporary key from session state after saving
            st.session_state.validated_api_key = None
        except Exception as e:
            st.error(f"❌ Erro ao salvar configurações: {e}")
