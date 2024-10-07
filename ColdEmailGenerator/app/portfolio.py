import pandas as pd
import chromadb
import os
import uuid
import logging

class Portfolio:
    def __init__(self):
        self.client = chromadb.PersistentClient('vectorstore')
        self.collection = None

    def load_portfolio(self):
        """Load portfolio data and populate vector database."""
        df = pd.read_csv('ColdEmailGenerator/app/resource/my_portfolio.csv')
        self.collection = self.client.get_or_create_collection(name="portfolio")
        if not self.collection.count():
            logging.info("Populating vector database...")
            for _, row in df.iterrows():
                self.collection.add(
                    documents=row["Techstack"],
                    metadatas={"links": row["Links"]},
                    ids=[str(uuid.uuid4())]
                )
            logging.info("Vector database populated successfully")
        else:
            logging.info("Vector database already populated")

    def query_links(self, skills):
        """Query the vector database for relevant portfolio links."""
        try:
            result = self.collection.query(query_texts=skills, n_results=2)
            return result.get('metadatas', [])
        except Exception as e:
            logging.error(f"Error querying vector database: {str(e)}")
            return []
