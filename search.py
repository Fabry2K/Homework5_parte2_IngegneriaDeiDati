import os
from lxml import html
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

from auxiliar_indexing_functions import clean_date

load_dotenv()


class Search:
    def __init__(self):
        self.es = Elasticsearch(
            os.getenv('ELASTIC_URL', 'http://localhost:9200'),
            verify_certs=False
        )
        self.index_name = 'hwk5_dataing'

    def ping(self):
        return self.es.ping()

    def create_index(self):
        self.es.indices.delete(index=self.index_name, ignore_unavailable=True)
        self.es.indices.create(index=self.index_name, body={
            'mappings': {
                'properties': {
                    'titolo': {'type': 'text'},
                    'abstract': {'type': 'text'},
                    'data': {'type': 'date', 'format': 'yyyy-MM-dd'},
                    'autori': {'type': 'text'},
                    'testo': {'type': 'text'}
                }
            }
        })

    def docs(self):
        documents = []
        html_path = os.path.join('.', 'articoli_html')

        for file in os.listdir(html_path):
            if not file.endswith('.html'):
                continue

            full_path = os.path.join(html_path, file)
            with open(full_path, 'r', encoding='utf-8') as f:
                tree = html.fromstring(f.read())

                titolo = tree.xpath("//title/text()")
                abstract = tree.xpath("//section[@class='abstract']/p")
                data = tree.xpath("//div[@class='display-inline-block']/following-sibling::text()[1]")
                autori = tree.xpath("//meta[@name='citation_author']/@content")
                paragraphs = tree.xpath(
                    "//section[@aria-label='Article content']"
                    "//p[not(ancestor::section[contains(@class,'abstract')])"
                    " and not(ancestor::table)"
                    " and not(ancestor::figure)]"
                )
                
                titolo = titolo[0].strip() if titolo else ""
                # Rimuove eventuale "-PMC" finale
                if "- PMC" in titolo:
                    titolo = titolo.rsplit("- PMC", 1)[0].strip()

                abstract = [p.text_content().strip() for p in abstract if p.text_content().strip()]
                testo = "\n\n".join(" ".join(p.itertext()).strip()for p in paragraphs)
                data = clean_date(" ".join(d.strip() for d in data if d.strip()))

                documents.append({
                    '_index': self.index_name,
                    '_source': {
                        'titolo': titolo,
                        'abstract': abstract,
                        'data': data,
                        'autori': autori,
                        'testo': testo
                    }
                })

        return documents

    def insert_documents(self):
        documents = self.docs()
        for doc in documents:
            self.es.index(index=self.index_name, body=doc['_source'])

        print(f"[ARTICLES] Indicizzati {len(documents)} articoli")

    def search(self, **query_args):
        return self.es.search(index=self.index_name, **query_args)

    def retrieve_document(self, id):
        return self.es.get(index=self.index_name, id=id)
