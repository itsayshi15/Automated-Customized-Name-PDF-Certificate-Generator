"""
generate_certificates.py
-------------------------
Generates certificates from a spreadsheet onto a fixed PDF template.
Supports custom TTF/OTF fonts, duplicate detection, auto-text scaling,
full row accounting, and large batch runs (280+ recipients).
"""

import json
import os
import re
import sys
from io import BytesIO

try:
    import pandas as pd
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError as e:
    print(f"Missing library: {e.name}")
    print("Install the required libraries with THIS exact command, then run the script again:")
    print(f'  "{sys.executable}" -m pip install pypdf reportlab openpyxl pandas')
    sys.exit(1)


def load_config(path="config.json"):
    if not os.path.exists(path):
        print(f"ERROR: '{path}' not found. Run this script from inside the certgen folder.")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def register_custom_font(cfg):
    """Registers the custom font if font_path is provided in config.json."""
    font_path = cfg.get("font_path")
    font_name = cfg.get("font_name", "Helvetica-Bold")

    if font_path:
        if not os.path.exists(font_path):
            print(f"ERROR: Custom font file '{font_path}' not found.")
            sys.exit(1)
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            print(f"Successfully registered font: '{font_name}'")
        except Exception as e:
            print(f"ERROR: Could not register font '{font_name}': {e}")
            sys.exit(1)
    return font_name


def load_names(sheet_path, column):
    """Loads names from sheet and reports total raw rows, non-empty entries, and unique counts."""
    if not os.path.exists(sheet_path):
        print(f"ERROR: sheet file '{sheet_path}' not found. Check sheet_path in config.json.")
        sys.exit(1)
    if sheet_path.lower().endswith(".csv"):
        df = pd.read_csv(sheet_path)
    else:
        df = pd.read_excel(sheet_path)

    if column not in df.columns:
        print(f"ERROR: column '{column}' not found. Available columns: {list(df.columns)}")
        sys.exit(1)

    # 1. Total raw rows in the column
    raw_rows = len(df[column])

    # 2. Cleaned non-empty entries
    raw_names = [str(n).strip() for n in df[column].dropna().tolist()]
    valid_names = [n for n in raw_names if n and n.lower() != "nan"]
    valid_count = len(valid_names)

    # 3. Unique names
    unique_names = list(dict.fromkeys(valid_names))
    unique_count = len(unique_names)
    
    # Empty and duplicate counts
    empty_rows = raw_rows - valid_count
    duplicates_count = valid_count - unique_count

    print("\n--- Name Processing Summary ---")
    print(f"Total rows in Excel sheet   : {raw_rows}")
    print(f"Empty/invalid rows skipped  : {empty_rows}")
    print(f"Total valid entries loaded  : {valid_count}")
    print(f"Duplicates omitted          : {duplicates_count}")
    print(f"Unique certificates to make : {unique_count}")
    print("-------------------------------\n")

    return unique_names


def safe_filename(name):
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    return cleaned.strip()


def make_text_overlay(width, height, text, cfg, font_name):
    """Creates a standalone overlay PDF buffer with auto-scaled font size."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))

    base_font_size = cfg.get("font_size", 28)
    color = cfg.get("color", [0, 0, 0])
    x = cfg["x"]
    y = cfg["y"]
    align = cfg.get("align", "center")

    # Set maximum allowed width (default: 80% of page width unless specified in config)
    max_text_width = cfg.get("max_text_width", width * 0.8)

    # 1. Calculate and auto-scale font size if text is too wide
    current_font_size = base_font_size
    text_width = pdfmetrics.stringWidth(text, font_name, current_font_size)

    if text_width > max_text_width:
        current_font_size = base_font_size * (max_text_width / text_width)
        print(f"  [Auto-scale] Scaling down '{text}' from {base_font_size}pt to {current_font_size:.1f}pt")

    # 2. Draw text with final font size
    c.setFont(font_name, current_font_size)
    c.setFillColorRGB(*color)

    if align == "center":
        c.drawCentredString(x, y, text)
    elif align == "right":
        c.drawRightString(x, y, text)
    else:
        c.drawString(x, y, text)

    c.save()
    buf.seek(0)
    return buf


def generate_single_certificate(template_path, name, cfg, font_name, out_path):
    """Generates a single individual certificate directly to disk."""
    template_reader = PdfReader(template_path)
    template_page = template_reader.pages[0]

    width = float(template_page.mediabox.width)
    height = float(template_page.mediabox.height)

    overlay_buf = make_text_overlay(width, height, name, cfg, font_name)
    overlay_reader = PdfReader(overlay_buf)
    overlay_page = overlay_reader.pages[0]

    template_page.merge_page(overlay_page)

    writer = PdfWriter()
    writer.add_page(template_page)

    with open(out_path, "wb") as f:
        writer.write(f)


def build_combined_pdf(pdf_files, output_path):
    """Combines individual PDFs page-by-page, closing file handles immediately to conserve RAM."""
    combined_writer = PdfWriter()
    for pdf_file in pdf_files:
        with open(pdf_file, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                combined_writer.add_page(page)

    with open(output_path, "wb") as f:
        combined_writer.write(f)


def main():
    cfg = load_config()
    font_name = register_custom_font(cfg)

    template_path = cfg["template_path"]
    sheet_path = cfg["sheet_path"]

    if not os.path.exists(template_path):
        print(f"ERROR: template file '{template_path}' not found. Check template_path in config.json.")
        sys.exit(1)

    name_column = cfg.get("name_column", "Name")
    output_dir = cfg.get("output_dir", "Certificates")

    os.makedirs(output_dir, exist_ok=True)

    names = load_names(sheet_path, name_column)
    if not names:
        print("No valid names found in the sheet. Check name_column in config.json.")
        sys.exit(1)

    print(f"Generating certificates for {len(names)} unique recipient(s)...")

    generated_files = []

    for i, name in enumerate(names, start=1):
        out_path = os.path.join(output_dir, f"{safe_filename(name)}.pdf")
        
        # 1. Generate individual certificate PDF
        generate_single_certificate(template_path, name, cfg, font_name, out_path)
        generated_files.append(out_path)

        print(f"  [{i}/{len(names)}] Created: {out_path}")

    # 2. Build the master combined file efficiently after all files are generated
    print("\nMerging all certificates into single master PDF...")
    combined_path = os.path.join(output_dir, "ALL_CERTIFICATES.pdf")
    build_combined_pdf(generated_files, combined_path)

    print(f"\nDone! All {len(names)} certificates successfully created in '{output_dir}/'")
    print(f"Combined master file: {combined_path}")


if __name__ == "__main__":
    main()