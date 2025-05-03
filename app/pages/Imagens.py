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
if "prompt_components" not in st.session_state:
    st.session_state.prompt_components = {
        "base_prompt": "",
        "style": "",
        "colors": "",
        "lighting": "",
        "composition": "",
    }


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


def build_prompt() -> str:
    """Constrói o prompt final com base nos componentes selecionados."""
    components = []

    if st.session_state.prompt_components["base_prompt"]:
        components.append(st.session_state.prompt_components["base_prompt"])
    if st.session_state.prompt_components["style"]:
        components.append(st.session_state.prompt_components["style"])
    if st.session_state.prompt_components["colors"]:
        components.append(st.session_state.prompt_components["colors"])
    if st.session_state.prompt_components["lighting"]:
        components.append(st.session_state.prompt_components["lighting"])
    if st.session_state.prompt_components["composition"]:
        components.append(st.session_state.prompt_components["composition"])

    return ", ".join(components)


# Título principal
st.title("🎨 Estúdio de Imagens")

# Seção de upload
uploaded_files = st.file_uploader(
    "Envie imagens (PNG, JPEG ou WebP, máximo 25MB cada)",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
)

# Construtor de Prompt
st.header("Construtor de Prompt")

# Prompt base
col1, col2 = st.columns([3, 1])
with col1:
    base_prompt = st.text_area(
        "Prompt Base",
        value=st.session_state.prompt_components["base_prompt"],
        help="Descreva o elemento principal da sua imagem",
    )
    st.session_state.prompt_components["base_prompt"] = base_prompt

with col2:
    template = st.selectbox("Usar Template", ["Nenhum", *list(IMAGE_GENERATION.keys())])
    if template != "Nenhum":
        st.session_state.prompt_components["base_prompt"] = IMAGE_GENERATION[template]

# Componentes do prompt
st.subheader("Elementos Adicionais")
col1, col2, col3, col4 = st.columns(4)

with col1:
    style = st.selectbox("Estilo Artístico", ["Nenhum", *list(ARTISTIC_STYLES.keys())])
    if style != "Nenhum":
        st.session_state.prompt_components["style"] = ARTISTIC_STYLES[style]
    else:
        st.session_state.prompt_components["style"] = ""

with col2:
    colors = st.selectbox("Paleta de Cores", ["Nenhum", *list(COLOR_PALETTES.keys())])
    if colors != "Nenhum":
        st.session_state.prompt_components["colors"] = COLOR_PALETTES[colors]
    else:
        st.session_state.prompt_components["colors"] = ""

with col3:
    lighting = st.selectbox("Iluminação", ["Nenhum", *list(LIGHTING.keys())])
    if lighting != "Nenhum":
        st.session_state.prompt_components["lighting"] = LIGHTING[lighting]
    else:
        st.session_state.prompt_components["lighting"] = ""

with col4:
    composition = st.selectbox("Composição", ["Nenhum", *list(COMPOSITION.keys())])
    if composition != "Nenhum":
        st.session_state.prompt_components["composition"] = COMPOSITION[composition]
    else:
        st.session_state.prompt_components["composition"] = ""

# Preview do prompt final
st.subheader("Prompt Final")
final_prompt = build_prompt()
st.text_area("", value=final_prompt, height=100, disabled=True)

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

    if submit_button and final_prompt:
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
                                prompt=final_prompt,
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
                            prompt=final_prompt,
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
