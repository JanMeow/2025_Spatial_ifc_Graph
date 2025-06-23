import json
from deep_translator import GoogleTranslator
from fpdf import FPDF
import fitz  
from pathlib import Path


file_path = Path("data/pdf")
pdf_file = file_path / "VFK_13-15.pdf"
doc = fitz.open(pdf_file)
text = doc[0].get_text()

if text.strip():
    print("✅ PDF contains selectable text.")
else:
    print("⚠️ PDF appears to be scanned or image-based (no text found).")


def translate_from_texttract(result_file:str):
    with open("result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    # === Step 2: Organize lines by page ===
    page_texts = {}
    for block in data["Blocks"]:
        if block["BlockType"] == "LINE":
            page_number = block["Page"]
            text = block.get("Text", "").strip()
            if text:
                page_texts.setdefault(page_number, []).append(text)
    # === Step 3: Translate text blocks page by page ===
    translated_pages = {}
    for page_num, lines in page_texts.items():
        german_text = "\n".join(lines)
        chunks = [german_text[i:i+4500] for i in range(0, len(german_text), 4500)]
        translated_chunks = [GoogleTranslator(source="de", target="en").translate(chunk) for chunk in chunks]
        translated_text = "\n".join(translated_chunks)
        translated_pages[page_num] = translated_text
    # === Step 4: Write to a PDF ===
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for page_num in sorted(translated_pages.keys()):
        pdf.add_page()
        pdf.multi_cell(0, 10, translated_pages[page_num])
    pdf.output("translated_output.pdf")
    print("✅ Translated PDF saved as 'translated_output.pdf'")