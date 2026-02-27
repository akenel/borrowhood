"""Generate SVG placeholder images for seed items.

Each SVG has a colored gradient background and an icon/emoji related to the item.
"""

import os

ITEMS = {
    "cookie-cutters": {"emoji": "&#127850;", "label": "Cookie Cutters", "colors": ["#f59e0b", "#d97706"]},
    "kitchenaid": {"emoji": "&#127860;", "label": "Stand Mixer", "colors": ["#ef4444", "#dc2626"]},
    "recipe-book": {"emoji": "&#128214;", "label": "Recipe Book", "colors": ["#8b5cf6", "#7c3aed"]},
    "bosch-drill": {"emoji": "&#128295;", "label": "Drill Set", "colors": ["#3b82f6", "#2563eb"]},
    "floor-jack": {"emoji": "&#128663;", "label": "Floor Jack", "colors": ["#ef4444", "#b91c1c"]},
    "welder": {"emoji": "&#9889;", "label": "Welder", "colors": ["#f97316", "#ea580c"]},
    "camping-table": {"emoji": "&#9978;", "label": "Camping Table", "colors": ["#10b981", "#059669"]},
    "garden-tools": {"emoji": "&#127793;", "label": "Garden Tools", "colors": ["#22c55e", "#16a34a"]},
    "garden-lesson": {"emoji": "&#127807;", "label": "Garden Lesson", "colors": ["#84cc16", "#65a30d"]},
    "wood-lathe": {"emoji": "&#129717;", "label": "Wood Lathe", "colors": ["#a16207", "#92400e"]},
    "circular-saw": {"emoji": "&#128296;", "label": "Circular Saw", "colors": ["#0ea5e9", "#0284c7"]},
    "3d-printer": {"emoji": "&#128424;", "label": "3D Printer", "colors": ["#6366f1", "#4f46e5"]},
    "phone-repair": {"emoji": "&#128241;", "label": "Phone Repair", "colors": ["#14b8a6", "#0d9488"]},
    "pottery-wheel": {"emoji": "&#127912;", "label": "Pottery Wheel", "colors": ["#e11d48", "#be123c"]},
    "watercolor-kit": {"emoji": "&#127912;", "label": "Watercolor Kit", "colors": ["#ec4899", "#db2777"]},
    "pasta-machine": {"emoji": "&#127837;", "label": "Pasta Machine", "colors": ["#f59e0b", "#b45309"]},
    "mountain-bike": {"emoji": "&#128692;", "label": "Mountain Bike", "colors": ["#ef4444", "#991b1b"]},
    "surfboard": {"emoji": "&#127940;", "label": "Surfboard", "colors": ["#06b6d4", "#0891b2"]},
    "carpet-cleaner": {"emoji": "&#129529;", "label": "Carpet Cleaner", "colors": ["#eab308", "#ca8a04"]},
    "pressure-washer": {"emoji": "&#128167;", "label": "Pressure Washer", "colors": ["#eab308", "#a16207"]},
}

SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{color2};stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#bg)" rx="8"/>
  <text x="200" y="130" text-anchor="middle" font-size="64" fill="white" opacity="0.9">{emoji}</text>
  <text x="200" y="190" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="white" opacity="0.95">{label}</text>
  <text x="200" y="218" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="white" opacity="0.6">BorrowHood</text>
</svg>"""

outdir = "src/static/images/seed"
os.makedirs(outdir, exist_ok=True)

for name, info in ITEMS.items():
    svg = SVG_TEMPLATE.format(
        color1=info["colors"][0],
        color2=info["colors"][1],
        emoji=info["emoji"],
        label=info["label"],
    )
    # Save as SVG
    with open(f"{outdir}/{name}.svg", "w") as f:
        f.write(svg)
    print(f"  {name}.svg")

print(f"\n{len(ITEMS)} SVG placeholders generated in {outdir}/")
