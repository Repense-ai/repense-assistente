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
