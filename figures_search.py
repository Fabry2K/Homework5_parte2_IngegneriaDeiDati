import os
import re
from lxml import html
from urllib.parse import urljoin

from auxiliar_indexing_functions import estrazione_mentions

from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()


class FigureSearch:
    def __init__(self):
        self.es = Elasticsearch(
            os.getenv('ELASTIC_URL', 'http://localhost:9200'),
            verify_certs=False
        )
        self.index_name = 'hwk5_figures'

    def ping(self):
        return self.es.ping()

    ############################
    #### Creazione indice #####
    ############################

    def create_index(self):
        self.es.indices.delete(index=self.index_name, ignore_unavailable=True)
        self.es.indices.create(index=self.index_name, body={
            'mappings': {
                'properties': {
                    'paper_id': {'type': 'keyword'},
                    'fig_id': {'type': 'keyword'},
                    'url': {'type': 'keyword'},
                    'caption': {'type': 'text'},
                    'mention': {'type': 'text'}
                }
            }
        })

    ############################
    #### Indicizzazione #######
    ############################

    def docs(self):
        documents = []
        html_path = os.path.join('.', 'articoli_html')

        for file in os.listdir(html_path):
            if not file.endswith('.html'):
                continue

            paper_id = file.replace('.html', '')
            full_path = os.path.join(html_path, file)

            with open(full_path, 'r', encoding='utf-8') as f:
                tree = html.fromstring(f.read())

                figures = tree.xpath("//figure")
                paragraphs = [p for p in tree.xpath("//p") if p.text_content().strip()]

                for fig in figures:

                    # Estrazione caption
                    caption_list = fig.xpath(".//figcaption//text()")
                    caption = " ".join(c.strip() for c in caption_list if c.strip())

                    #Parole chiave caption
                    keywords = set(caption.split())

                    if not caption:
                        continue

                    # # Escludi tabelle e algoritmi
                    # if re.match(r'^(TABLE|Table|ALGORITHM|Algorithm)\b', caption):
                    #     continue

                    # URL immagine
                    url_list = fig.xpath(".//img/@src")
                    url = url_list[0] if url_list else None

                    # Estrai numero figura (se presente)
                    fig_id = None
                    m = fig.get('id', 'NO_ID')
                    if m:
                        fig_id = m

                    mention = estrazione_mentions(tree, fig_id)

                    documents.append({
                        '_index': self.index_name,
                        '_source': {
                            'paper_id': paper_id,
                            'fig_id': fig_id,
                            'url': url,
                            'caption': caption,
                            'mention': mention
                        }
                    })

        return documents

    def insert_documents(self):
        documents = self.docs()

        for doc in documents:
            self.es.index(index=self.index_name, body=doc['_source'])

        print(f"[FIGURES] Indicizzate {len(documents)} figure")

    ############################
    #### Query ################
    ############################

    def search(self, **query_args):
        return self.es.search(index=self.index_name, **query_args)
