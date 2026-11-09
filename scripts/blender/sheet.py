"""Tile review stills into one contact sheet (system Python, needs Pillow).

    python3 sheet.py OUT.png COLS IMG [IMG ...]

Every image is scaled to the height of the first; rows are left-aligned.
"""
import sys

from PIL import Image


def main(out, cols, paths, gap=8, bg=(18, 18, 18)):
    ims = [Image.open(p).convert("RGB") for p in paths]
    h = ims[0].height
    ims = [im if im.height == h else im.resize((round(im.width * h / im.height), h)) for im in ims]
    rows = [ims[i:i + cols] for i in range(0, len(ims), cols)]
    width = max(sum(im.width for im in row) + gap * (len(row) - 1) for row in rows)
    sheet = Image.new("RGB", (width, h * len(rows) + gap * (len(rows) - 1)), bg)
    for j, row in enumerate(rows):
        x = 0
        for im in row:
            sheet.paste(im, (x, j * (h + gap)))
            x += im.width + gap
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3:])
