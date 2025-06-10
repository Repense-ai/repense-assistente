import streamlit as st
from pathlib import Path

# --- Page Configuration ---
st.set_page_config(
    page_title="Bem-vindo à Repense.ai",
    page_icon="👋",
    layout="centered"
)

# --- UI Elements ---
st.image(
    "https://repense.ai/wp-content/uploads/2024/10/Repense_laranja_fundo_transparente-1024x576.png",
    width=200,
)

st.title("Bem-vindo ao seu Assistente Inteligente")
st.markdown(
    """
    Transforme a comunicação com seus clientes. Este aplicativo permite que você configure e gerencie um assistente de IA para automatizar interações e fornecer suporte instantâneo.
    """
)

st.divider()

st.markdown("#### Primeiros Passos")
col1, col2 = st.columns(2)

with col1:
    if st.button("Acessar Configurações", use_container_width=True, type="primary"):
        st.switch_page("pages/Configurações.py")

with col2:
    if st.button("Abrir Interface do Assistente", use_container_width=True):
        st.switch_page("pages/Assistente.py")

st.divider()

st.markdown(
    """
    <div style="text-align: center;">
        <p>É hora de repensar. Junte-se a nós nessa jornada para construir um mundo mais justo e eficiente.</p>
    </div>
    """,
    unsafe_allow_html=True
)
