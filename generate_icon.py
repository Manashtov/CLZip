from pathlib import Path
from PIL import Image

def build_icon():
    root = Path(__file__).resolve().parent
    assets = root / "assets"
    
    if not assets.exists():
        print("Error: No se encontró el directorio assets/")
        return

    # Resoluciones estándar que exige Windows
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for s in sizes:
        p = assets / f"icon_{s}.png"
        if not p.exists():
            p = assets / f"clzip_logo_{s}x{s}.png"
        
        if p.exists():
            img = Image.open(p).convert("RGBA")
            if img.size != (s, s):
                img = img.resize((s, s), Image.Resampling.LANCZOS)
            images.append(img)
            print(f" [+] Añadida capa: {p.name} ({s}x{s})")
        else:
            print(f" [!] Aviso: falta tamaño {s}x{s}")

    if not images:
        print("Error: No se encontraron imágenes PNG en assets/")
        return

    out_ico = assets / "icon.ico"
    images[0].save(
        out_ico,
        format="ICO",
        append_images=images[1:]
    )
    print(f"\n✓ Icono multicapa creado con éxito en: {out_ico}")
    print(f"  Tamaño final: {out_ico.stat().st_size} bytes")

if __name__ == "__main__":
    build_icon()