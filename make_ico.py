from pathlib import Path
from PIL import Image

assets_dir = Path("assets")

# Tamaños estándar en orden
sizes = [16, 32, 48, 64, 128, 256]
images = []

# Cargar las imágenes individuales si existen
for s in sizes:
    p = assets_dir / f"icon_{s}.png"
    if p.exists():
        img = Image.open(p).convert("RGBA")
        images.append(img)

# Si no están todas por separado, usamos la de 512 como base
if not images:
    base = Image.open(assets_dir / "icon.png").convert("RGBA")
    images = [base.resize((s, s), Image.Resampling.LANCZOS) for s in sizes]

# Guardar como archivo .ico multi-resolución
output_ico = assets_dir / "icon.ico"
images[0].save(
    str(output_ico),
    format="ICO",
    sizes=[(img.width, img.height) for img in images],
    append_images=images[1:]
)

print(f"✓ Archivo creado con éxito en: {output_ico.resolve()}")