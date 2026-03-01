#!/bin/bash
# Generate seed images using Pollinations.ai free API
# Each image is a simple product photo, 400x300px
set -e

DIR="src/static/images/seed"
mkdir -p "$DIR"

declare -A IMAGES
IMAGES[cookie-cutters]="professional cookie cutter set on wooden table, product photo, white background"
IMAGES[kitchenaid]="red KitchenAid stand mixer on kitchen counter, product photo"
IMAGES[recipe-book]="cookbook cover with cookies, warm cozy kitchen background"
IMAGES[bosch-drill]="blue Bosch cordless drill set in case, product photo"
IMAGES[floor-jack]="red hydraulic floor jack with jack stands, garage workshop"
IMAGES[welder]="MIG welding machine with helmet and gloves, workshop"
IMAGES[camping-table]="folding camping table with chairs outdoors, nature"
IMAGES[garden-tools]="garden tools spade rake hoe arranged neatly, product photo"
IMAGES[garden-lesson]="elderly woman teaching gardening in vegetable garden"
IMAGES[wood-lathe]="professional wood lathe in woodworking workshop"
IMAGES[circular-saw]="circular saw with guide on workbench, product photo"
IMAGES[3d-printer]="3D printer on workbench, maker space"
IMAGES[phone-repair]="smartphone repair on workbench with precision tools"
IMAGES[pottery-wheel]="pottery wheel with clay bowls in art studio"
IMAGES[watercolor-kit]="watercolor paint set with brushes and paper, art supplies"
IMAGES[pasta-machine]="vintage pasta machine on kitchen table, Italian kitchen"
IMAGES[mountain-bike]="red mountain bike leaning against stone wall"
IMAGES[surfboard]="white and blue surfboard on sandy beach"
IMAGES[carpet-cleaner]="yellow professional carpet cleaning machine, product photo"
IMAGES[pressure-washer]="yellow pressure washer with accessories, product photo"

for name in "${!IMAGES[@]}"; do
    if [ -f "$DIR/$name.jpg" ]; then
        echo "SKIP $name.jpg (exists)"
        continue
    fi
    prompt="${IMAGES[$name]}"
    encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$prompt'))")
    url="https://image.pollinations.ai/prompt/${encoded}?width=400&height=300&nologo=true&seed=42"
    echo "GET  $name.jpg ..."
    curl -sL "$url" -o "$DIR/$name.jpg" 2>&1
    echo "OK   $name.jpg ($(wc -c < "$DIR/$name.jpg") bytes)"
    sleep 1  # be nice to the API
done

echo "--- Done. $(ls "$DIR"/*.jpg 2>/dev/null | wc -l) images generated."
