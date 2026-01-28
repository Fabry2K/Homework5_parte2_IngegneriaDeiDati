import os
from lxml import html

# =========================
# CONFIGURAZIONE
# =========================
HTML_DIR = "articoli_html"
TABLE_XPATH = "//section[@class='tw xbox font-sm']"

# =========================
# FUNZIONI
# =========================

def extract_tables(html_file):
    """
    Estrae id, caption e contenuto delle tabelle in un articolo.
    """
    with open(html_file, "r", encoding="utf-8") as f:
        tree = html.fromstring(f.read())

    tables = tree.xpath(TABLE_XPATH)
    result = []

    for fig in tables:
        table_id = fig.get("id", "NO_ID")

        # Caption: div.caption se esiste, altrimenti primo figlio
        caption = " ".join(
            c.strip()
            for c in fig.xpath("(./div[@class='caption'] | ./*[1])//text()")
            if c.strip()
        )

        # Contenuto testuale della table dentro div.tbl-box
        table_nodes = fig.xpath(".//div[contains(@class,'tbl-box')]/table")
        table_content = []

        for tn in table_nodes:
            rows = tn.xpath(".//tr")
            table_rows = []
            for r in rows:
                # prende tutte le celle <td> e <th> della riga
                cells = r.xpath(".//th | .//td")
                cell_texts = [c.text_content().strip() for c in cells]
                if cell_texts:
                    table_rows.append(cell_texts)
            table_content.append(table_rows)

        result.append({
            "table_id": table_id,
            "caption": caption,
            "tables_content": table_content
        })

    return result

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
        tables = extract_tables(filepath)

        print(f"\n=== Article ID: {filename} ===")

        if not tables:
            print("No tables found")
            continue

        for i, t in enumerate(tables, 1):
            print(f"\n[{i}] Section ID: {t['table_id']}")
            print(f"Caption: {t['caption'] if t['caption'] else 'No caption'}")

            if t['tables_content']:
                for j, table_rows in enumerate(t['tables_content'], 1):
                    print(f"\nTable {j} content:")
                    for row in table_rows:
                        # stampa le celle separate da tab
                        print("\t".join(row))
            else:
                print("No table found")

if __name__ == "__main__":
    main()
