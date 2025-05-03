from typing import Any

import streamlit as st

from app.prompts.templates import (
    ARTISTIC_STYLES,
    COLOR_PALETTES,
    COMPOSITION,
    IMAGE_GENERATION,
    LIGHTING,
)
from src.image import OpenAIImages, get_memory_buffer

# Configuração da página
st.set_page_config(page_title="Estúdio de Imagens IA", page_icon="🎨", layout="wide")

# Inicializa variáveis de estado da sessão
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []
if "image_costs" not in st.session_state:
    st.session_state.image_costs = []
if "openai_client" not in st.session_state:
    st.session_state.openai_client = None
if "prompt" not in st.session_state:
    st.session_state.prompt = ""


def validate_file(uploaded_file: Any) -> bool:
    """Valida os requisitos do arquivo."""
    if uploaded_file is None:
        return False

    file_type = uploaded_file.type.lower()
    valid_types = ["image/png", "image/jpeg", "image/webp"]
    if file_type not in valid_types:
        st.error("Por favor, envie apenas arquivos PNG, JPEG ou WebP.")
        return False

    if uploaded_file.size > 25 * 1024 * 1024:
        st.error("O arquivo deve ter menos de 25MB.")
        return False

    return True


def initialize_openai_client() -> bool:
    """Inicializa o cliente OpenAI."""
    try:
        st.session_state.openai_client = OpenAIImages()
        return True
    except Exception as e:
        st.error(f"Erro ao inicializar o cliente OpenAI: {e!s}")
        return False


def format_cost(cost: float) -> str:
    """Formata o custo em dólares."""
    return f"US$ {cost:.4f}"


# Título principal
st.title("🎨 Estúdio de Imagens")

# Seção de upload
uploaded_files = st.file_uploader(
    "Envie imagens (PNG, JPEG ou WebP, máximo 25MB cada)",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
)

# Layout do prompt e popover
st.header("Prompt para Geração de Imagem")


prompt = st.text_area(
    "Digite seu prompt",
    value=st.session_state.prompt,
    height=150,
    help="Descreva detalhadamente a imagem que você deseja gerar",
    placeholder="Ex: Uma paisagem serena de montanhas ao pôr do sol, com cores vibrantes e estilo impressionista...",
)

st.session_state.prompt = prompt

with st.popover("📝 Sugestões"):
    # Seletor de categoria
    category = st.radio(
        "Escolha uma categoria:",
        [
            "Templates",
            "Estilos Artísticos",
            "Composição",
            "Paletas de Cores",
            "Iluminação",
        ],
        horizontal=True,
        key="category_selector",
    )

    st.markdown("---")

    # Container com scroll para as sugestões
    with st.container():
        category_map = {
            "Templates": (IMAGE_GENERATION, "🎯"),
            "Estilos Artísticos": (ARTISTIC_STYLES, "🎨"),
            "Composição": (COMPOSITION, "🖼️"),
            "Paletas de Cores": (COLOR_PALETTES, "🌈"),
            "Iluminação": (LIGHTING, "💡"),
        }

        if category in category_map:
            items, icon = category_map[category]
            for name, value in items.items():
                with st.expander(f"{icon} {name}"):
                    st.code(value, language=None)

# Formulário principal
with st.form("image_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        size = st.selectbox(
            "Tamanho da Imagem", ["1024x1024", "1536x1024", "1024x1536"]
        )
    with col2:
        quality = st.selectbox(
            "Qualidade",
            ["low", "medium", "high"],
            format_func=lambda x: {"low": "Baixa", "medium": "Média", "high": "Alta"}[
                x
            ],
        )
    with col3:
        background = st.selectbox(
            "Fundo",
            ["auto", "transparent", "opaque"],
            format_func=lambda x: {
                "auto": "Automático",
                "transparent": "Transparente",
                "opaque": "Opaco",
            }[x],
        )

    submit_button = st.form_submit_button("Processar Imagem")

    if submit_button and prompt:
        if not st.session_state.openai_client and not initialize_openai_client():
            st.error("Falha ao inicializar o cliente OpenAI")
        else:
            with st.spinner("Processando..."):
                try:
                    if uploaded_files:
                        valid_files = [f for f in uploaded_files if validate_file(f)]
                        if len(valid_files) > 16:
                            st.error("Máximo de 16 imagens permitido.")
                        elif valid_files:
                            image_buffers = [
                                get_memory_buffer(f.read(), f.name) for f in valid_files
                            ]

                            result = st.session_state.openai_client.edit(
                                prompt=prompt,
                                image=image_buffers,
                                size=size,
                                quality=quality,
                                background=background,
                            )

                            st.session_state.generated_images.append(result)
                            st.session_state.image_costs.append(
                                st.session_state.openai_client.cost
                            )
                            st.success("Imagem processada com sucesso!")
                    else:
                        result = st.session_state.openai_client.generate(
                            prompt=prompt,
                            size=size,
                            quality=quality,
                            background=background,
                        )
                        st.session_state.generated_images.append(result)
                        st.session_state.image_costs.append(
                            st.session_state.openai_client.cost
                        )
                        st.success("Imagem gerada com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao processar imagem: {e!s}")

# Exibe imagens geradas e custos
if st.session_state.generated_images:
    st.header("Resultados")

    # Mostra custo total
    total_cost = sum(st.session_state.image_costs)
    with st.sidebar:
        st.markdown(
            "Custo Total 💰",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='text-align:center; font-size:1.5em; color:#10b981; font-weight:bold;'>"
            f"{format_cost(total_cost)}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

    # Cria colunas para exibir imagens
    cols = st.columns(4)  # 4 imagens por linha
    for idx, (image_bytes, cost) in enumerate(
        zip(
            st.session_state.generated_images,
            st.session_state.image_costs,
            strict=False,
        )
    ):
        with cols[idx % 4]:
            st.image(image_bytes, caption=f"Imagem {idx + 1}")
            st.caption(f"Custo: {format_cost(cost)}")

            # Botão de download
            btn = st.download_button(
                label="Baixar Imagem",
                data=image_bytes,
                file_name=f"imagem_gerada_{idx + 1}.png",
                mime="image/png",
            )

# Botão para limpar a sessão
if st.session_state.generated_images:
    if st.sidebar.button("Limpar Todas as Imagens"):
        st.session_state.generated_images = []
        st.session_state.image_costs = []
        st.rerun()
