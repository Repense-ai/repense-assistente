"""
Script para criar um ícone simples para o instalador
Requer Pillow: pip install Pillow
"""

try:
    import os

    from PIL import Image, ImageDraw, ImageFont

    def create_simple_icon():
        """Cria um ícone simples para o instalador"""

        # Criar imagem 256x256
        size = 256
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Fundo circular azul
        margin = 20
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=(52, 152, 219, 255),
            outline=(41, 128, 185, 255),
            width=4,
        )

        # Texto "RA" (Repense Assistente)
        try:
            # Tentar usar fonte do sistema
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            # Fallback para fonte padrão
            font = ImageFont.load_default()

        text = "RA"

        # Calcular posição centralizada do texto
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (size - text_width) // 2
        y = (size - text_height) // 2 - 10

        # Desenhar texto branco
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

        # Salvar como ICO
        icon_path = "icon.ico"

        # Criar múltiplos tamanhos para o ICO
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icons = []

        for icon_size in sizes:
            resized = img.resize(icon_size, Image.Resampling.LANCZOS)
            icons.append(resized)

        # Salvar como ICO com múltiplos tamanhos
        icons[0].save(
            icon_path, format="ICO", sizes=[(icon.width, icon.height) for icon in icons]
        )

        print(f"Ícone criado: {icon_path}")
        return True

    if __name__ == "__main__":
        if os.path.exists("icon.ico"):
            print("Ícone já existe: icon.ico")
        else:
            create_simple_icon()

except ImportError:
    print("Pillow não está instalado. Para criar um ícone personalizado, instale com:")
    print("pip install Pillow")
    print("Ou adicione manualmente um arquivo icon.ico neste diretório.")
