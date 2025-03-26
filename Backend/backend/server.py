from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
import os

app = FastAPI()

# Connect to Elasticsearch
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
es = Elasticsearch([ELASTICSEARCH_HOST])
INDEX_NAME = "documents"

# Ensure index exists
def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body={
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "text": {"type": "text"}
                }
            }
        })
create_index()

# Initialize with default documents
@app.get("/init")
def init_data():
    docs = [
        {"id": "1", "text": "India is a country in South Asia. It is the seventh-largest country by land area."},
        {"id": "2", "text": "India is the most populous country as of 2023, and the world's largest democracy."},
        {"id": "3", "text": "The Indian subcontinent was home to the Indus Valley Civilization."},
        {"id": "4", "text": "India gained independence from British rule in 1947, led by Mahatma Gandhi."}
    ]
    for doc in docs:
        es.index(index=INDEX_NAME, id=doc["id"], document=doc)
    return {"message": "Documents inserted successfully"}

# Insert document
@app.get("/insert/{query}")
def insert_document(query: str):
    doc_id = str(hash(query))  # Generate unique ID
    doc = {"id": doc_id, "text": query}
    res = es.index(index=INDEX_NAME, id=doc_id, document=doc)
    return {"result": res["result"], "id": doc_id}

# Get document by query
@app.get("/get/{query}")
def get_document(query: str):
    res = es.search(index=INDEX_NAME, body={
        "query": {"match": {"text": query}}
    })
    return {"hits": res["hits"]["hits"]}
