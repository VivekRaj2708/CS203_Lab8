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
