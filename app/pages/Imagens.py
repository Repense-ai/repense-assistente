import json
import os

import redis
import streamlit as st

from app.prompts.templates import (
    ARTISTIC_STYLES,
    COLOR_PALETTES,
    COMPOSITION,
    IMAGE_GENERATION,
    LIGHTING,
)
from src.image import OpenAIImages, get_memory_buffer
from src.memory import RedisManager

# Configuração da página
st.set_page_config(page_title="Estúdio de Imagens IA", page_icon="🎨", layout="wide")

# Initialize Redis client
try:
    redis_client = redis.Redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True
    )
    redis_client.ping()  # Check connection
except redis.exceptions.ConnectionError as e:
    st.error(
        f"Não foi possível conectar ao Redis. Verifique se os serviços estão rodando. Detalhes: {e}"
    )
    st.stop()

# --- API Key and Client Initialization ---
openai_api_key_manager = RedisManager(redis_client, "secrets:openai_api_key")
api_key = openai_api_key_manager.get_memory_dict().get('key')

if not api_key:
    st.warning("⚠️ A chave da API da OpenAI não foi configurada.")
    if st.button("Ir para Configurações"):
        st.switch_page("pages/Configurações.py")
    st.stop()

# Initialize OpenAI client and store in session state
if "openai_client" not in st.session_state:
    try:
        st.session_state.openai_client = OpenAIImages(api_key=api_key)
    except Exception as e:
        st.error(
            f"A chave de API configurada é inválida ou expirou. Por favor, atualize-a na página de configurações. Erro: {e}"
        )
        if st.button("Ir para Configurações"):
            st.switch_page("pages/Configurações.py")
        st.stop()

# Initialize config manager
config_manager = RedisManager(redis_client, "config")
config = config_manager.get_memory_dict()

# Initialize Redis Manager for saved prompts
prompts_manager = RedisManager(redis_client, "saved_prompts")

# Inicializa variáveis de estado da sessão
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []
if "image_costs" not in st.session_state:
    st.session_state.image_costs = []
if "prompt" not in st.session_state:
    st.session_state.prompt = ""
if "saved_prompts" not in st.session_state:
    st.session_state.saved_prompts = prompts_manager.get_memory_dict()

def save_prompt(name: str, prompt_text: str) -> bool:
    """Salva um novo prompt no Redis."""
    try:
        current_prompts = st.session_state.saved_prompts
        current_prompts[name] = prompt_text
        prompts_manager.set_memory_dict(current_prompts)
        st.session_state.saved_prompts = current_prompts  # Update session state
        return True
    except Exception as e:
        st.error(f"Erro ao salvar prompt: {e}")
        return False

def delete_prompt(name: str) -> bool:
    """Deleta um prompt salvo do Redis."""
    try:
        current_prompts = st.session_state.saved_prompts
        if name in current_prompts:
            del current_prompts[name]
            prompts_manager.set_memory_dict(current_prompts)
            st.session_state.saved_prompts = current_prompts  # Update session state
        return True
    except Exception as e:
        st.error(f"Erro ao deletar prompt: {e}")
        return False

def format_cost(cost: float) -> str:
    """Formata o custo em dólares."""
    return f"US$ {cost:.4f}"

# Sidebar para gerenciar prompts salvos
with st.sidebar:
    st.header("Prompts Salvos")

    # Seção para salvar novo prompt
    with st.expander("💾 Salvar Prompt Atual"):
        prompt_name = st.text_input("Nome do Prompt", key="new_prompt_name")
        if st.button("Salvar") and prompt_name and st.session_state.prompt:
            if save_prompt(prompt_name, st.session_state.prompt):
                st.success(f"Prompt '{prompt_name}' salvo com sucesso!")

    # Seção para carregar prompts
    if st.session_state.saved_prompts:
        st.markdown("### Carregar Prompt")
        for name, saved_prompt in list(st.session_state.saved_prompts.items()):
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📜 {name}", key=f"load_{name}"):
                    st.session_state.prompt = saved_prompt
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{name}"):
                    if delete_prompt(name):
                        st.success(f"Prompt '{name}' deletado!")
                        st.rerun()

    st.markdown("---")

# Título principal
st.title("🎨 Estúdio de Imagens")

# Seção de upload
uploaded_files = st.file_uploader(
    "Envie até 16 imagens (PNG, JPEG ou WebP, máximo 25MB cada)",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
)

# Layout do prompt e popover
st.header("Prompt para Geração de Imagem")

st.session_state.new_prompt = st.text_area(
    "Digite seu prompt",
    value=st.session_state.prompt,
    height=150,
    help="Descreva detalhadamente a imagem que você deseja gerar",
    placeholder="Ex: Uma paisagem serena de montanhas ao pôr do sol, com cores vibrantes e estilo impressionista...",
)

if st.session_state.new_prompt != st.session_state.prompt:
    st.session_state.prompt = st.session_state.new_prompt
    st.rerun()

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

    if submit_button and st.session_state.prompt:
        if not st.session_state.openai_client:
            st.error("Cliente OpenAI não inicializado. Verifique as configurações da API.")
        else:
            with st.spinner("Processando..."):
                try:
                    if uploaded_files:
                        if len(uploaded_files) > 16:
                            st.error("Máximo de 16 imagens permitido.")
                        elif uploaded_files:
                            image_buffers = [
                                get_memory_buffer(f.read(), f.name)
                                for f in uploaded_files
                            ]

                            result = st.session_state.openai_client.edit(
                                prompt=st.session_state.prompt,
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
                            prompt=st.session_state.prompt,
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
