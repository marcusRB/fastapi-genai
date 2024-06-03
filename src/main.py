from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import chromadb
from sqlalchemy.orm import Session
from src.db import SessionLocal, create_tables, InteractionLog

app = FastAPI()

# Initialize ChromaDB client
client = chromadb.Client()
collection = client.create_collection("embeddings")

# Load LLM
model_name = "gpt2"  # Change to an appropriate open-source model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Create database tables
create_tables()

class TextItem(BaseModel):
    text: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/embed/")
async def embed_text(item: TextItem, db: Session = Depends(get_db)):
    inputs = tokenizer(item.text, return_tensors="pt")
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state.mean(dim=1).cpu().numpy()
    collection.insert(embeddings=embeddings, documents=[item.text])
    log = InteractionLog(user_input=item.text, model_response="Embedded")
    db.add(log)
    db.commit()
    return {"message": "Text embedded and stored successfully."}

@app.get("/query/")
async def query_text(q: str = Query(..., description="Query text"), db: Session = Depends(get_db)):
    inputs = tokenizer(q, return_tensors="pt")
    with torch.no_grad():
        query_embedding = model(**inputs).last_hidden_state.mean(dim=1).cpu().numpy()
    results = collection.search(query_embeddings=query_embedding, n_results=1)
    if results:
        log = InteractionLog(user_input=q, model_response=results[0]["document"])
        db.add(log)
        db.commit()
        return {"response": results[0]["document"]}
    raise HTTPException(status_code=404, detail="No relevant document found.")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI GenAI service"}
