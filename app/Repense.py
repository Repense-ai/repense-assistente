import streamlit as st
import os
from pathlib import Path

# Logo and Title
st.image(
    "https://repense.ai/wp-content/uploads/2024/10/Repense_laranja_fundo_transparente-1024x576.png",
    width=200,
)

# Description
st.markdown(
    """
### Nascemos da insatisfação com o status quo.

Um mundo onde sistemas falham, processos são ineficientes e as pessoas são colocadas em segundo plano.

Somos uma chama de mudança, um catalisador para um futuro mais justo e eficiente.

### É hora de repensar.

Não aceitamos o mundo como ele é. Queremos mudá-lo.

Com inteligência artificial, temos a oportunidade de olhar para o mundo com novos olhos.

Vamos desafiar o convencional e buscar novas formas de fazer as coisas.

Vamos usar tecnologia para resolver problemas reais e equilibrar as relações de poder.

Somos pensadores, somos inquietos, somos agentes de transformação.

**Junte-se a nós nessa jornada para construir um mundo mais justo e eficiente.**
"""
)

st.divider()

if st.button("Começar"):
    st.switch_page("pages/Configurações.py")


def get_app_version():
    """Reads the version from the VERSION file."""
    try:
        # The VERSION file is in the same directory as this script
        version_file = Path(__file__).parent / "VERSION"
        return version_file.read_text().strip()
    except FileNotFoundError:
        return "N/A"


with st.sidebar:
    st.page_link("pages/Assistente.py", label="Assistente Virtual", icon="🤖")
    st.page_link("pages/Imagens.py", label="Estúdio de Imagens", icon="🎨")
    st.page_link("pages/Configurações.py", label="Configurações", icon="⚙️")
    st.info(
        "Certifique-se de que sua chave de API da OpenAI esteja configurada para usar os assistentes."
    )
    st.markdown("---")
    st.markdown(f"Versão: `{get_app_version()}`")
