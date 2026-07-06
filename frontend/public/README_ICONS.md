# Icon files

## Important

Create these files for full PWA support:

- `icon-192x192.png` — required
- `icon-512x512.png` — required
- `badge-72x72.png` — optional (`icon-192x192.png` is used as fallback)

## Quick setup

### Online tools (recommended)

1. Visit https://realfavicongenerator.net/ or https://www.pwabuilder.com/imageGenerator
2. Upload a 512×512 source icon
3. Download the generated assets
4. Place files in `frontend/public/`

### Python script (requires Pillow)

```python
from PIL import Image, ImageDraw, ImageFont


def create_icon(size, filename):
    img = Image.new("RGB", (size, size), color="#f5e6e8")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size // 3)
    except OSError:
        font = ImageFont.load_default()

    text = "EC"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size - text_width) // 2, (size - text_height) // 2)
    draw.text(position, text, fill="#e8b4b8", font=font)
    img.save(filename)


create_icon(192, "icon-192x192.png")
create_icon(512, "icon-512x512.png")
```

### Temporary placeholders

Until final icons exist, you can use:

1. Solid-color backgrounds
2. Simple text marks
3. Exports from an existing logo

## Current status

- `manifest.json` references icon paths
- Service Worker uses the main icon as badge fallback
- Icon PNG files still need to be added

See `ICON_GUIDE.md` for design guidelines.
