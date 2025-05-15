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
redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True
)

# Initialize OpenAI client
client = OpenAI()

# Initialize Redis manager for persistent chat history
chat_manager = RedisManager(redis_client, "chat_history")
config_manager = RedisManager(redis_client, "config")

stored_messages = chat_manager.get_memory_dict()
config = config_manager.get_memory_dict()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": PROMPT_ASSISTENTE.format(**config)},
    ]

# Load stored messages into session state if available
if stored_messages and "messages" in stored_messages:
    if not st.session_state.messages:  # Only load if session is empty
        st.session_state.messages = stored_messages["messages"]

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
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

            # Make API call
            response = client.chat.completions.create(
                model="gpt-4.1",  # Using the latest model
                messages=messages,
                stream=True,  # Enable streaming
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
            st.error(f"Error: {e!s}")

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
            [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages]
        )

        st.download_button(
            "📥 Baixar",
            chat_text,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
        )
