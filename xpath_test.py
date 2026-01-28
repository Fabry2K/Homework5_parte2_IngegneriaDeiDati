import os
from lxml import html

# =========================
# CONFIGURAZIONE
# =========================
HTML_DIR = "articoli_html"

# XPath
TITLE_XPATH = "//title/text() | //hgroup/h1[@data-anchor-id='TRpt']/text()"
MAIN_TEXT_XPATH = (
    "//section[@id and not(contains(@class,'abstract')) "
    "and not(contains(@class,'tw xbox'))]//text()"
)

# =========================
# FUNZIONI
# =========================

def extract_title(tree):
    """
    Estrae il titolo dell'articolo.
    """
    title_nodes = tree.xpath(TITLE_XPATH)
    if title_nodes:
        return " ".join(t.strip() for t in title_nodes if t.strip())
    return "No title found"

def extract_main_text(tree):
    """
    Estrae il testo principale dell'articolo, escludendo abstract, tabelle e figure.
    """
    text_nodes = tree.xpath(MAIN_TEXT_XPATH)
    if text_nodes:
        return " ".join(t.strip() for t in text_nodes if t.strip())
    return "No main text found"

# =========================
# MAIN DI TEST
# =========================

def main():
    if not os.path.isdir(HTML_DIR):
        print(f"Directory '{HTML_DIR}' non trovata.")
        return

    for filename in sorted(os.listdir(HTML_DIR)):
        if not filename.endswith(".html"):
            continue

        filepath = os.path.join(HTML_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            tree = html.fromstring(f.read())

        title = extract_title(tree)
        main_text = extract_main_text(tree)

        print(f"\n=== Article ID: {filename} ===")
        print(f"Title: {title}")
        print(f"Main text (first 500 chars): {main_text[:500]}...\n")  # tronca per leggibilità

if __name__ == "__main__":
    main()
