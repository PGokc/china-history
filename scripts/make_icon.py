from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Design/Brand/AppIconMaster.png"
OUTPUT = ROOT / "App/Assets.xcassets/AppIcon.appiconset/AppIcon.png"

with Image.open(SOURCE) as image:
    icon = image.convert("RGB").resize((1024, 1024), Image.Resampling.LANCZOS)
    icon.save(OUTPUT, optimize=True)
