import os
from lxml import html
import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# =========================
# CONFIGURAZIONE
# =========================
HTML_DIR = "articoli_html"
TABLE_XPATH = "//section[@class='tw xbox font-sm']"


def debug_sections(tree):
    sections = tree.xpath("//section[.//h2[contains(@class,'pmc_sec_title')]]"
                          "[not(.//section[contains(@class,'abstract')])]")

    print(f"SEZIONI TROVATE: {len(sections)}\n")

    for i, s in enumerate(sections, 1):
        sec_id = s.get("id", "NO_ID")
        classes = s.get("class", "NO_CLASS")

        title = s.xpath(".//h2[1]/text()")
        title = title[0].strip() if title else "NO TITLE"

        print(f"[{i}] id={sec_id} | class={classes}")
        print(f"    title: {title}\n")


# =========================
# FUNZIONI
# =========================

def extract_tables(html_file):
    """
    Estrae solo id e caption delle tabelle in un articolo (non il contenuto).
    """
    with open(html_file, "r", encoding="utf-8") as f:
        tree = html.fromstring(f.read())

    tables = tree.xpath(TABLE_XPATH)
    result = []

    for fig in tables:
        table_id = fig.get("id", "NO_ID")
        caption = " ".join(
            c.strip()
            for c in fig.xpath("(./div[@class='caption'] | ./*[1])//text()")
            if c.strip()
        )
        result.append({
            "table_id": table_id,
            "caption": caption if caption else "No caption"
        })

    return result


def estrazione_context_paragraphs(tree, keywords):

    STOP_WORDS = set(ENGLISH_STOP_WORDS)
    context_paragraphs = []

    sections = tree.xpath("//section[.//h2[contains(@class,'pmc_sec_title')]]"
                            "[not(.//section[contains(@class,'abstract')])]")

    keywords = {k.lower() for k in keywords if k.lower() not in STOP_WORDS}

    for s in sections:

        title = s.xpath("./h2")
        text = s.xpath(".//p")

        section_title = title[0].text_content().strip() if title else ""
        section_text = " ".join(
            t.text_content().strip()
            for t in text
            if t.text_content().strip()
        )

        section_tokens = {
            w.lower()
            for w in re.findall(r"\b[a-zA-Z0-9\-]+\b", section_text)
        }

        if keywords & section_tokens:
            context_paragraphs.append(section_title)

    return context_paragraphs


# =========================
# MAIN DI TEST
# =========================

def main():

    if not os.path.isdir(HTML_DIR):
        print(f"Directory '{HTML_DIR}' non trovata.")
        return

    # Keywords di esempio per test
    keywords = ["cardiovascular"]

    for filename in sorted(os.listdir(HTML_DIR)):
        if not filename.endswith(".html"):
            continue

        filepath = os.path.join(HTML_DIR, filename)

    # with open(filepath, "r", encoding="utf-8") as f:
    #     tree = html.fromstring(f.read())

    # debug_sections(tree)

        # -------------------------
        # Estrazione tabelle (solo id e caption)
        # -------------------------
        tables = extract_tables(filepath)
        print(f"\n=== Article ID: {filename} ===")
        if not tables:
            print("No tables found")
        else:
            for i, t in enumerate(tables, 1):
                print(f"[{i}] Table ID: {t['table_id']}, Caption: {t['caption']}")

        # -------------------------
        # Estrazione sezioni con parole chiave
        # -------------------------
        with open(filepath, "r", encoding="utf-8") as f:
            tree = html.fromstring(f.read())

        sections_with_keywords = estrazione_context_paragraphs(tree, keywords)
        if sections_with_keywords:
            print("\nSections containing keywords:")
            for st in sections_with_keywords:
                print(f"- {st}")
        else:
            print("No sections matched keywords.")


if __name__ == "__main__":
    main()
