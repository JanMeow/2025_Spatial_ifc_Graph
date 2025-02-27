from pathlib import Path
from text_extractor import extract_text
from var import open_ai_key

# Load pdf
pdf_folder = Path("data/pdf")
pdf_path = pdf_folder/"sample.pdf"

# Get Api Key which should be saved from your env file
open_ai_key = open_ai_key

def main():
    # Extract text from pdf
    content = extract_text(pdf_path, sort_by={"type":"title", "title_font_size":15})
    # print(content[2])


    # Currently 
    
    return




if __name__ == "__main__":
    main()