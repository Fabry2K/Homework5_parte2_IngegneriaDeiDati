import os
import asyncio
from playwright.async_api import async_playwright

async def scrape_pmc_flexible(limit=500):
    # Query flessibile: OR permette di trovare i termini separatamente
    query = '("ultra-processed foods") AND ("cardiovascular risk")'
    query_encoded = query.replace(' ', '+').replace('"', '%22')
    # URL aggiornato al nuovo dominio PMC
    base_url = f"https://pmc.ncbi.nlm.nih.gov/search/?term={query_encoded}&filter=collections.open_access"
    
    if not os.path.exists("articoli_html"):
        os.makedirs("articoli_html")

    async with async_playwright() as p:
        print("Avvio browser...")
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        page = await context.new_page()
        
        links_recuperati = set()
        current_page = 1

        print(f"Ricerca iniziata su: {base_url}")

        # Fase 1: Raccolta Link
        while len(links_recuperati) < limit:
            print(f"Esploro pagina risultati {current_page}... (Trovati: {len(links_recuperati)})")
            try:
                await page.goto(f"{base_url}&page={current_page}", timeout=60000)
                
                # Aspettiamo che i risultati siano caricati (usiamo un selettore più generico e robusto)
                # Il nuovo PMC usa spesso 'section.result' o link che contengono '/articles/PMC...'
                await page.wait_for_selector("a[href*='/articles/PMC']", timeout=15000)
                
                # Estraiamo tutti i link che portano ad articoli PMC
                hrefs = await page.eval_on_selector_all(
                    "a[href*='/articles/PMC']", 
                    "elements => elements.map(e => e.href)"
                )
                
                initial_count = len(links_recuperati)
                for href in hrefs:
                    # Filtriamo per assicurarci che siano link diretti agli articoli e non a citazioni
                    if "/articles/PMC" in href and "pdf" not in href.lower():
                        # Puliamo l'URL da eventuali parametri extra
                        clean_url = href.split("?")[0].rstrip("/")
                        links_recuperati.add(clean_url)
                    if len(links_recuperati) >= limit:
                        break
                
                if len(links_recuperati) == initial_count:
                    print("Nessun nuovo link trovato. Potresti aver raggiunto la fine dei risultati.")
                    break
                    
                current_page += 1
                await asyncio.sleep(2) 
                
            except Exception as e:
                print(f"Errore durante la scansione della pagina {current_page}: {e}")
                break

        print(f"\nRaccolta completata. Link totali unici: {len(links_recuperati)}")

        # Fase 2: Download HTML
        for i, url in enumerate(list(links_recuperati)):
            try:
                print(f"[{i+1}/{len(links_recuperati)}] Scaricamento: {url}")
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                
                # Prendiamo il contenuto della pagina
                content = await page.content()
                pmcid = url.split("/")[-1]
                
                with open(f"articoli_html/{pmcid}.html", "w", encoding="utf-8") as f:
                    f.write(content)
                
                await asyncio.sleep(1) 
            except Exception as e:
                print(f"Errore su {url}: {e}")

        await browser.close()
        print(f"\nFinito! Cartella: {os.path.abspath('articoli_html')}")

if __name__ == "__main__":
    asyncio.run(scrape_pmc_flexible(500))