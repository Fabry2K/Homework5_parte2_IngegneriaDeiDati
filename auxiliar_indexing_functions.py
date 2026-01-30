from datetime import datetime
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import re

def clean_date(text):
    """
    Estrae la data dal testo e la ritorna in formato YYYY-MM-DD.
    Se non trova una data valida, ritorna None.
    """
    if not text:
        return None

    text = text.strip()

    # Cerca una data nel formato "2014 Sep 12"
    match = re.search(r"\b(\d{4})\s+([A-Za-z]{3})\s+(\d{1,2})\b", text)
    if not match:
        return None

    year, month_str, day = match.groups()

    # Converte il mese abbreviato in numero
    try:
        month = datetime.strptime(month_str, "%b").month
    except ValueError:
        return None

    # Restituisce la data in formato YYYY-MM-DD
    return f"{year}-{month:02d}-{int(day):02d}"


def clean_abstract(abstract):
    # Rimuove la parola "Abstract" all'inizio
    return re.sub(r'^\s*Abstract\s*', '', abstract, flags=re.IGNORECASE)

def text_extraction(tree):
    parts = []

    nodes = tree.xpath(
        "//section[@aria-label='Article content']//*[self::h2 or self::p]"
        "[not(ancestor::section[contains(@class,'abstract')])]"
    )

    for n in nodes:
        text = n.text_content().strip()
        if text:
            if n.tag == "h2":
                # Wrappa in <h3> per titolo evidenziato
                parts.append(f"<h3>{text}</h3>")
            else:
                # Paragrafo normale, senza grassetto
                parts.append(f"<p>{text}</p>")

    return "\n".join(parts)



####################
######tabelle#######
####################
def estrazione_paper_id(tree):

    # Estrae il testo che contiene "PMCID:"
    text = tree.xpath("//div/text()[contains(., 'PMCID:')]")[0].strip()

    # Estrae solo il PMCID
    pmcid = text.split("PMCID:")[1].split()[0]  # primo token dopo "PMCID:"

    return pmcid



def estrazione_context_paragraphs(tree, keywords):

    STOP_WORDS = set(ENGLISH_STOP_WORDS)
    context_paragraphs = []

    sections = tree.xpath("//section[.//h2[contains(@class,'pmc_sec_title')]]"
                            "[not(.//section[contains(@class,'abstract')])]")

    keywords = {k.lower() for k in keywords if k.lower() not in STOP_WORDS}

    for s in sections:

        min_matches = max(1, len(keywords) // 7)

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

        matched = keywords & section_tokens
        if len(matched)>=min_matches:
            context_paragraphs.append(section_title)

    return context_paragraphs




#funzione che estrae, per ogni tabella, la lista di paragrafi che la menzionano
def estrazione_mentions(tree, table_id):

    mentions_paragraphs = []

    sections = tree.xpath("//section[.//h2[contains(@class,'pmc_sec_title')]]"
                            "[not(.//section[contains(@class,'abstract')])]")

    for s in sections:

        #prima analisi della sezione
        title = s.xpath("./h2")
        mentions = s.xpath(f".//p[.//a[contains(@href, '#{table_id}')]]")

        section_title = title[0].text_content().strip() if title else ""
        
        if mentions:
            mentions_paragraphs.append(section_title)
        
    return mentions_paragraphs