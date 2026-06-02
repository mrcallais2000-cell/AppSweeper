#!/bin/bash
# Converts assets/icon.svg → assets/icon.icns
# Requires: librsvg  (brew install librsvg)
#           OR ImageMagick (brew install imagemagick)

SVG="assets/icon.svg"
ICONSET="assets/icon.iconset"
ICNS="assets/icon.icns"

mkdir -p "${ICONSET}"

gen() {
    local SIZE=$1
    local OUT="${ICONSET}/icon_${SIZE}x${SIZE}.png"
    if command -v rsvg-convert &>/dev/null; then
        rsvg-convert -w "${SIZE}" -h "${SIZE}" "${SVG}" -o "${OUT}"
    elif command -v convert &>/dev/null; then
        convert -density 300 -background none \
                -resize "${SIZE}x${SIZE}" "${SVG}" "${OUT}"
    else
        echo "Error: install librsvg or ImageMagick first"
        echo "  brew install librsvg"
        exit 1
    fi
}

echo "→ Generating PNG sizes from SVG..."
for S in 16 32 128 256 512; do
    gen "${S}"
    DOUBLE=$((S * 2))
    [ "${DOUBLE}" -le 1024 ] && cp \
        "${ICONSET}/icon_${S}x${S}.png" \
        "${ICONSET}/icon_${S}x${S}@2x.png" 2>/dev/null || true
done

# Correct macOS iconset naming for @2x
cp "${ICONSET}/icon_32x32.png"   "${ICONSET}/icon_16x16@2x.png"
cp "${ICONSET}/icon_64x64.png"   "${ICONSET}/icon_32x32@2x.png"  2>/dev/null || true
cp "${ICONSET}/icon_256x256.png" "${ICONSET}/icon_128x128@2x.png"
cp "${ICONSET}/icon_512x512.png" "${ICONSET}/icon_256x256@2x.png"

echo "→ Converting to .icns..."
iconutil -c icns "${ICONSET}" -o "${ICNS}"
rm -rf "${ICONSET}"
echo "✓ Created: ${ICNS}"
