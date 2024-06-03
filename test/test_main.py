from fastapi.testclient import TestClient
from src.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base, get_db, InteractionLog

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FastAPI GenAI service"}

def test_embed_text():
    response = client.post("/embed/", json={"text": "This is a test text."})
    assert response.status_code == 200
    assert response.json() == {"message": "Text embedded and stored successfully."}

def test_query_text():
    client.post("/embed/", json={"text": "This is a test text."})
    response = client.get("/query/", params={"q": "test"})
    assert response.status_code == 200
    assert "response" in response.json()
