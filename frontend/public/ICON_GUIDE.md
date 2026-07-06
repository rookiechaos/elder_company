# PWA icon guide

## Required files

| File | Size | Purpose |
|------|------|---------|
| `icon-192x192.png` | 192×192 | Android home screen |
| `icon-512x512.png` | 512×512 | Splash screen, high-DPI |
| `badge-72x72.png` | 72×72 | Push notification badge (optional) |

## Brand colors

- Theme: `#f5e6e8` (light pink)
- Accent: `#e8b4b8` (pink)
- Background: `#faf9f7` (warm off-white)

## Design guidelines

- **Maskable**: content should sit in the safe zone (~80% center) for adaptive icons
- **Simple**: readable at small sizes
- **On-brand**: reflect care collaboration (heart, hands, or “EC” monogram)
- **Gradient option**: `#f5e6e8` → `#e8b4b8`

## How to generate

### Option 1 — online

Use [PWA Asset Generator](https://github.com/onderceylan/pwa-asset-generator) or similar tools with a 512×512 source.

### Option 2 — design tools

Create in Figma, Sketch, or Illustrator; export exact PNG sizes.

### Option 3 — CLI

```bash
npm install -g pwa-asset-generator
pwa-asset-generator source-icon.png public/ --icon-only
```

## File location

```
elder_company/frontend/public/
├── icon-192x192.png
├── icon-512x512.png
└── badge-72x72.png   # optional
```

## Verification checklist

1. Each file is reasonably sized (preferably under 100 KB)
2. Icons render correctly on target devices
3. Installed PWA shows the correct icon
4. Maskable safe zone respected (if applicable)

## Notes

- Missing icons can break PWA install
- Paths must match `manifest.json`
- Update icons when branding changes

## Temporary fallback

Before final artwork, use solid backgrounds, simple geometry, or a simplified logo mark.
