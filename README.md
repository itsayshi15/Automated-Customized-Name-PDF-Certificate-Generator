# Automated Customized Name PDF Certificate Generator

This is a Python application that creates personalized PDF certificates automatically. It reads names from an Excel or CSV file and places them onto a PDF certificate background template. It supports custom fonts, automatic text resizing, duplicate removal, and produces a merged master PDF.

---

## File Organization & Naming Rules

To run this project correctly without errors, all project files must be placed inside the **same main project folder**:

```
certificate-generator/
│
├── generate_certificates.py  # Main Python script
├── find_position.py          # Grid script to find text location
├── config.json               # Project settings file
├── template.pdf              # Blank certificate background file
├── names.xlsx                # Spreadsheet containing recipient names
├── font.ttf                  # Custom font file
└── Certificates/             # Output folder (created automatically)
    ├── ALL_CERTIFICATES.pdf  # Merged file containing all certificates
    ├── John_Doe.pdf          # Individual certificate file
    └── ...
```

>  **IMPORTANT RULE:** The file names written in your `config.json` file must **match your actual file names exactly**. This includes uppercase and lowercase letters as well as file extensions (like `.pdf` or `.xlsx`).

---

## Why Use This Project?

* **Saves Time:** Creating certificates manually for many people takes a lot of time. This script generates hundreds of certificates in just a few seconds.
* **Prevents Errors:** Copying names manually can cause spelling mistakes. This project takes names directly from your spreadsheet.
* **Fits Long Names:** If a person has a long name, the script automatically reduces the font size so it fits inside the certificate design smoothly.
* **Two Output Options:** It saves individual files for each recipient and also creates one big master file containing all certificates for easy printing.

---

## Features

1. **Customize Recipient Names:** Change the text color, font size, position, and alignment (`center`, `left`, or `right`) easily.
2. **Spreadsheet Support:** Works with both Excel (`.xlsx`) and CSV (`.csv`) files.
3. **Position Helper Tool (`find_position.py`):** Draws red grid lines with coordinate numbers on your PDF template so you can find where to write the name.
4. **Auto Text Resizing:** Automatically reduces font size if a name is too wide for the page.
5. **Custom Font File Support:** Supports TrueType (`.ttf`) and OpenType (`.otf`) custom font files.
6. **Data Cleaning:** Automatically removes empty rows, invalid entries, and duplicate names.
7. **Merged Master PDF:** Combines all generated certificates into a single file named `ALL_CERTIFICATES.pdf`.

---

## How It Is Different From Other Tools

* **No Text Overlap:** Basic tools cut off long names or draw text over borders. This script measures text width and resizes it automatically.
* **Visual Grid Tool:** You do not need to guess coordinate numbers. The included grid tool shows exact `(X, Y)` positions clearly.
* **Runs Fast and Uses Low Memory:** It generates large batches of certificates without slowing down your computer.

---

## Step-by-Step Setup & Usage Guide (VS Code)

Follow these simple steps from start to finish using Visual Studio Code.

### Step 1: Open Project in VS Code
1. Download or clone this project folder to your computer.
2. Open **VS Code**.
3. Click `File` > `Open Folder...` and select your project folder.
4. Make sure all scripts, your template PDF, spreadsheet file, font file, and `config.json` are in this same main folder.
5. Open the integrated terminal by pressing `Ctrl + ~` (or `Cmd + ~` on Mac) or clicking `Terminal` > `New Terminal`.

### Step 2: Install Required Libraries
In the VS Code terminal, run this command to install all necessary Python libraries:

```bash
pip install pypdf reportlab openpyxl pandas
```

### Step 3: Find Name Position (`find_position.py`)
1. Place your empty certificate template PDF into the main folder (e.g., `template.pdf`).
2. Run this command in your VS Code terminal:

   ```bash
   python find_position.py template.pdf
   ```

3. Open the newly created `template_grid.pdf` file.
4. Look at the red grid numbers on the blank line to find your `X` and `Y` coordinate numbers.

*Note: PDF coordinate systems start at `(0, 0)` in the **bottom-left** corner of the page.*

### Step 4: Configure `config.json`
Click `config.json` in VS Code and update your settings to match your files and target coordinates:

```json
{
  "template_path": "template.pdf",
  "sheet_path": "names.xlsx",
  "name_column": "Name",
  "output_dir": "Certificates",
  "font_path": "Playfair_Display/PlayfairDisplay-Italic-VariableFont_wght.ttf",
  "font_name": "PlayfairDisplay-Italic",
  "font_size": 28,
  "max_text_width": 400,
  "x": 300,
  "y": 360,
  "align": "center",
  "color": [0, 0, 0]
}
```

### Step 5: Run the Main Generator
Execute the main generation script in the VS Code terminal:

```bash
python generate_certificates.py
```

After the script finishes, open the `Certificates/` folder created in your file explorer. You will see:
* Individual PDF files for each person.
* A single `ALL_CERTIFICATES.pdf` master file containing all certificates.

---

## Config JSON Settings Explained

| Settings Key | Type | Explanation |
| :--- | :--- | :--- |
| `template_path` | Text | The file name of your blank certificate PDF template. |
| `sheet_path` | Text | The file name of your Excel or CSV list. |
| `name_column` | Text | The column heading name in your spreadsheet containing names. |
| `output_dir` | Text | The folder name where completed certificates are saved. |
| `font_path` | Text | The location path of your `.ttf` or `.otf` font file. |
| `font_name` | Text | A registered name for your custom font. |
| `font_size` | Number | Starting font size for the recipient names. |
| `max_text_width` | Number | Maximum width allowed before text is automatically scaled down. |
| `x` | Number | The horizontal position from the left side of the page. |
| `y` | Number | The vertical position from the bottom side of the page. |
| `align` | Text | Text alignment mode (`center`, `left`, or `right`). |
| `color` | List | RGB color numbers from 0 to 1 (e.g., `[0, 0, 0]` for black). |

---

## Troubleshooting

* **File Not Found Error:** Check if your file names in `config.json` match your actual filenames exactly.
* **Font Error:** Make sure your font file path is correct and points to a valid `.ttf` or `.otf` file.
* **Wrong Text Position:** Remember that higher `Y` values move text up, and lower `Y` values move text down on the page.
