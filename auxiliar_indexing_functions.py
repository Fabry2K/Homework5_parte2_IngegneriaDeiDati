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





####################
######tabelle#######
####################
def estrazione_context_paragraphs(tree, keywords):

    STOP_WORDS = set(ENGLISH_STOP_WORDS)
    context_paragraphs = []

    section = tree.xpath("//section[@class='ltx_section']")
    appendix = tree.xpath("//section[@class='ltx_appendix']")

    keywords = {k.lower() for k in keywords if k.lower() not in STOP_WORDS}

    #fisso un minimo di match per evitare falsi positivi
    min_matches = max(1, len(keywords) // 9)

    for s in section:

        #prima analisi della sezione
        section_title = " ".join(s.xpath("./*[starts-with(name(), 'h')]//text()")).strip()
        section_text = " ".join(s.xpath("./*[not(self::section)]//text()")).lower()

        #tokenizzo le parole nel paragrafo (eliminando così i duplicati)
        section_tokens = set(re.findall(r"\b[a-zA-Z0-9\-]+\b", section_text))

        matched = keywords & section_tokens

        if len(matched)>=min_matches:
            context_paragraphs.append(section_title)
        
       
       #ora si analizzano i paragrafi di sezione (se ci sono)
        paragraphs = s.xpath("./section")

        if paragraphs:
            for p in paragraphs:
                paragraph_title = " ".join(p.xpath("./*[starts-with(name(), 'h')]//text()")).strip()
                paragraph_text = " ".join(p.xpath(".//text()")).lower()

                #tokenizzo le parole nel paragrafo (eliminando così i duplicati)
                paragraph_tokens = set(re.findall(r"\b[a-zA-Z0-9\-]+\b", paragraph_text))

                matched = keywords & paragraph_tokens
            
                if len(matched)>=min_matches:
                    context_paragraphs.append(paragraph_title)
        
    if appendix:
        for a in appendix:
            app_title = " ".join(a.xpath("./*[starts-with(name(), 'h')][1]//text()")).strip()
            app_text = " ".join(a.xpath(".//text()")).lower()

            #tokenizzo le parole nel paragrafo (eliminando così i duplicati)
            app_tokens = set(re.findall(r"\b[a-zA-Z0-9\-]+\b", app_text))

            matched = keywords & app_tokens
        
            if len(matched)>=min_matches:
                context_paragraphs.append(app_title)


    return context_paragraphs



#funzione che estrae, per ogni tabella, la lista di paragrafi che la menzionano
def estrazione_mentions(tree, table_id):

    mentions_paragraphs = []

    section = tree.xpath("//section[@class='ltx_section']")
    appendix = tree.xpath("//section[@class='ltx_appendix']")

    for s in section:

        #prima analisi della sezione
        section_title = " ".join(s.xpath("./*[starts-with(name(), 'h')]//text()")).strip()
        mentions = s.xpath(f"./*[not(self::section)]//p[.//a[contains(@href, '#{table_id}')]]")
        
        if mentions:
            mentions_paragraphs.append(section_title)
        
       
        #ora si analizzano i paragrafi di sezione (se ci sono)
        paragraphs = s.xpath("./section")

        if paragraphs:
            for p in paragraphs:
                paragraph_title = " ".join(p.xpath("./*[starts-with(name(), 'h')]//text()")).strip()
                mentions = p.xpath(f".//p[.//a[contains(@href, '#{table_id}')]]")

                if mentions:
                    mentions_paragraphs.append(paragraph_title)
        
    if appendix:
        for a in appendix:
            app_title = " ".join(a.xpath("./*[starts-with(name(), 'h')][1]//text()")).strip()
            mentions = a.xpath(f".//p[.//a[contains(@href, '#{table_id}')]]")

            if mentions:
                mentions_paragraphs.append(app_title)


    return mentions_paragraphs