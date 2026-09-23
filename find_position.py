"""
find_position.py
-----------------
Overlays a coordinate grid on your certificate template PDF so you can
figure out exactly where (x, y) the name should be printed.

USAGE:
    python find_position.py template.pdf

OUTPUT:
    template_grid.pdf  -> same certificate, with a light grid + coordinate
                           labels drawn on top (every 50 points).

HOW TO USE THE OUTPUT:
    Open template_grid.pdf and find where the blank name line is.
    Read off the nearest grid labels to get an (x, y) estimate, e.g. (300, 260).
    Note: PDF coordinates start at (0, 0) in the BOTTOM-LEFT corner of the page,
    and increase upward and to the right.
    Plug that (x, y) into config.json as "x" and "y" for the name field.
"""

import sys
from io import BytesIO

try:
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
except ImportError as e:
    print(f"Missing library: {e.name}")
    print("Install the required libraries with THIS exact command, then run the script again:")
    print(f'  "{sys.executable}" -m pip install pypdf reportlab openpyxl pandas')
    sys.exit(1)


def make_grid_overlay(width, height, step=50):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    c.setStrokeColorRGB(1, 0, 0)
    c.setFillColorRGB(1, 0, 0)
    c.setLineWidth(0.3)
    c.setFont("Helvetica", 6)

    x = 0
    while x <= width:
        c.line(x, 0, x, height)
        c.drawString(x + 2, 4, str(int(x)))
        x += step

    y = 0
    while y <= height:
        c.line(0, y, width, y)
        c.drawString(2, y + 2, str(int(y)))
        y += step

    c.save()
    buf.seek(0)
    return buf


def main():
    if len(sys.argv) != 2:
        print("Usage: python find_position.py <template.pdf>")
        sys.exit(1)

    template_path = sys.argv[1]
    reader = PdfReader(template_path)
    page = reader.pages[0]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    overlay_buf = make_grid_overlay(width, height)
    overlay_page = PdfReader(overlay_buf).pages[0]

    page.merge_page(overlay_page)

    writer = PdfWriter()
    writer.add_page(page)

    out_path = template_path.rsplit(".", 1)[0] + "_grid.pdf"
    with open(out_path, "wb") as f:
        writer.write(f)

    print(f"Page size: {width} x {height} points")
    print(f"Grid overlay saved to: {out_path}")


if __name__ == "__main__":
    main()
