import fitz




def get_page_content(page, sort_by = {"type":"title", "title_font_size":15}):
    text_dict = page.get_text("dict")
    page_content = []

    if sort_by["type"] == "page":
        page_content.append({"title":"",
                             "text":page.get_text("text"),
                             "page_number":page.number})

    if sort_by["type"] == "title":
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    if "spans" in line:
                        for span in line["spans"]:
                            # print(span["size"], span["text"])
                            if span["size"] >= sort_by["title_font_size"]:
                                if len (page_content) >0:
                                    # Because sometimes the title are broken into few lines
                                        if page_content[-1]["text"] == "":
                                            page_content[-1]["title"] += span["text"]
                                            continue
                                dict_obj = {
                                    "title":span["text"],
                                    "text":""
                                }
                                page_content.append(dict_obj)
                            else:
                                if len(page_content) >0:
                                    # .replace because german documents have this weird thing
                                    cleaned = span["text"].replace("\xad", "")
                                    page_content[-1]["text"] += cleaned
    return page_content

  


# Extract text from pdf
def extract_text(pdf, sort_by):

    pdf = fitz.open(pdf)
    all_content = [None] * len(pdf)
    for i,page in enumerate(pdf):
        print(page.number)
        all_content[i] = get_page_content(page, sort_by)

    return all_content