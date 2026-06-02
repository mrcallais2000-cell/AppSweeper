#!/bin/bash
# ─────────────────────────────────────────────────────────────────
#  AppSweeper — Build Script
#  Produces: AppSweeper.app  +  AppSweeper-1.0.0.dmg
# ─────────────────────────────────────────────────────────────────
set -e

APPNAME="AppSweeper"
VERSION="1.0.0"
DMG="${APPNAME}-${VERSION}.dmg"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🧹 Building ${APPNAME} v${VERSION}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1 — Python deps
echo "→ Installing Python dependencies..."
pip3 install py2app --quiet --upgrade

# 2 — Generate .icns if missing
if [ ! -f "assets/icon.icns" ]; then
    echo "→ Generating icon.icns..."
    bash make_icon.sh
fi

# 3 — Clean
echo "→ Cleaning previous builds..."
rm -rf build dist "${DMG}"

# 4 — Build .app
echo "→ Building ${APPNAME}.app (py2app)..."
python3 setup.py py2app 2>&1 | grep -E "(error|warning|Building|Copying)" || true
echo "✓ Built: dist/${APPNAME}.app"

# 5 — Create .dmg
echo "→ Creating ${DMG}..."

if command -v create-dmg &>/dev/null; then
    # Polished DMG with drag-to-Applications (brew install create-dmg)
    create-dmg \
        --volname "${APPNAME}" \
        --volicon "assets/icon.icns" \
        --window-pos 200 140 \
        --window-size 580 380 \
        --icon-size 120 \
        --icon "${APPNAME}.app" 160 190 \
        --hide-extension "${APPNAME}.app" \
        --app-drop-link 420 190 \
        --no-internet-enable \
        "${DMG}" \
        "dist/"
else
    echo "  ⚠  create-dmg not found → brew install create-dmg (recommended)"
    echo "  → Using hdiutil fallback..."
    hdiutil create \
        -volname "${APPNAME}" \
        -srcfolder "dist/${APPNAME}.app" \
        -ov -format UDZO \
        "${DMG}"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Done! → ${DMG}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
