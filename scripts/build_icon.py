"""Generate the transparent, multi-resolution Necker cube application icon."""
from pathlib import Path
from PIL import Image, ImageDraw

PROJECT = Path(__file__).resolve().parents[1]
ASSETS = PROJECT / 'assets'
SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)
EDGES = (
    ((40, 96), (160, 96)), ((160, 96), (160, 216)),
    ((160, 216), (40, 216)), ((40, 216), (40, 96)),
    ((96, 40), (216, 40)), ((216, 40), (216, 160)),
    ((216, 160), (96, 160)), ((96, 160), (96, 40)),
    ((40, 96), (96, 40)), ((160, 96), (216, 40)),
    ((160, 216), (216, 160)), ((40, 216), (96, 160)),
)


def render(size):
    scale = 8
    image = Image.new('RGBA', (size * scale, size * scale))
    draw = ImageDraw.Draw(image)
    # A narrow pale outline keeps the wireframe legible on dark desktops.
    for width, color in ((14, '#ffffff'), (10, '#087e83')):
        stroke = max(1, round(width * size * scale / 256))
        radius = stroke / 2
        for edge in EDGES:
            points = [tuple(v * size * scale / 256 for v in p) for p in edge]
            draw.line(points, fill=color, width=stroke)
            for x, y in points:
                draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
    return image.resize((size, size), Image.Resampling.LANCZOS)


def main():
    frames = [render(size) for size in SIZES]
    frames[-1].save(ASSETS / 'necker-icon.png')
    frames[-1].save(ASSETS / 'necker.ico', sizes=[(s, s) for s in SIZES],
                    append_images=frames[:-1])
    lines = '\n'.join(f'    <path d="M {a[0]} {a[1]} L {b[0]} {b[1]}"/>'
                      for a, b in EDGES)
    (ASSETS / 'necker-icon.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">\n'
        '  <title>Necker cube</title>\n'
        '  <defs><g id="edges" fill="none" stroke-linecap="round">\n'
        + lines + '\n  </g></defs>\n'
        '  <use href="#edges" stroke="#ffffff" stroke-width="14"/>\n'
        '  <use href="#edges" stroke="#087e83" stroke-width="10"/>\n'
        '</svg>\n', encoding='utf-8')


if __name__ == '__main__':
    main()
