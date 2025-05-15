"""
Test page for Redis volume functionality.

This module provides a UI for testing Redis configuration and persistence.
"""

import os
from datetime import datetime
from pathlib import Path

import openai
import redis
import streamlit as st
from dotenv import load_dotenv, set_key

from src.memory import RedisManager

# Functions


def save_api_key(api_key: str) -> bool:
    """
    Save the API key to .env file and update environment.

    Args:
        api_key (str): The OpenAI API key to save

    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        env_path = Path(".env").resolve()
        st.write(f"Saving API key to: {env_path}")  # Debug info

        # Ensure the API key is properly formatted
        api_key = api_key.strip()

        # Use python-dotenv's set_key function which is more reliable
        set_key(str(env_path), "OPENAI_API_KEY", api_key)
        load_dotenv(str(env_path))  # Reload the .env file

        # Update environment variables
        os.environ["OPENAI_API_KEY"] = api_key
        openai.api_key = api_key

        # Verify the environment was updated
        if os.getenv("OPENAI_API_KEY") == api_key:
            st.write("Environment variable successfully updated")  # Debug info
            return True
        else:
            st.error("Environment variable not updated correctly")
            return False

    except Exception as e:
        st.error(f"Failed to save API key: {e!s}")
        return False


def validate_api_key(api_key: str) -> bool:
    """
    Validate if the provided API key is valid.

    Args:
        api_key (str): The OpenAI API key to validate

    Returns:
        bool: True if key is valid, False otherwise
    """
    try:
        api_key = api_key.strip()
        openai.api_key = api_key
        # Make a simple API call to test the key
        _ = openai.models.list()
        st.write("API key validation successful")  # Debug info
        return True
    except Exception as e:
        st.error(f"API key validation failed: {e!s}")
        return False


# Configure page
st.set_page_config(
    page_title="Repense.ai - Assistente", page_icon="🤖", layout="centered"
)

# API Key Management
st.header("Configuração da API OpenAI")

# Load existing API key
load_dotenv()
existing_key = os.getenv("OPENAI_API_KEY")

# Debug information
env_path = Path(".env").resolve()

if existing_key:
    st.success("✅ API Key da OpenAI já está configurada!")
    text = "Atualizar chave"
else:
    st.warning(
        "⚠️ API Key da OpenAI não está configurada. Por favor, configure-a abaixo."
    )
    text = "Salvar chave"


api_key = st.text_input(
    "Digite sua API Key da OpenAI",
    type="password",
    help="Você pode obter sua API key em: https://platform.openai.com/api-keys",
)

if st.button(text):
    if api_key:
        if validate_api_key(api_key):
            if save_api_key(api_key):
                st.success("✅ API Key salva com sucesso!")
            else:
                st.error("❌ Falha ao salvar a API Key.")
        else:
            st.error("❌ API Key inválida. Por favor, verifique e tente novamente.")
    else:
        st.error("❌ Por favor, insira uma API Key.")

st.divider()

# Initialize Redis client
redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True
)

# Initialize config manager
config_manager = RedisManager(redis_client, "config")

# Load existing configuration
current_config = config_manager.get_memory_dict() or {}

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

        try:
            config_manager.set_memory_dict(config_data)
            st.success("✅ Configurações salvas com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao salvar configurações: {e}")
