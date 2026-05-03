from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_empty_query():
    response = client.post("/api/search", json={"query": "", "query_type": "keywords"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Query cannot be empty"}

def test_valid_keyword_search():
    # Assuming the DB might be empty or not fully populated during the test,
    # we just want to ensure the endpoint doesn't crash and returns the correct schema.
    response = client.post("/api/search", json={"query": "transformer, attention", "query_type": "keywords"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "extracted_keywords" in data
    assert data["extracted_keywords"] == []

def test_special_characters_search():
    # Test handling of symbols like &, -, +
    response = client.post("/api/search", json={"query": "state-of-the-art & fast+efficient", "query_type": "keywords"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data

def test_abstract_search():
    abstract = "In this paper, we propose a novel transformer architecture with self-attention mechanism that achieves state-of-the-art results on several NLP benchmarks."
    response = client.post("/api/search", json={"query": abstract, "query_type": "abstract"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "extracted_keywords" in data
    # KeyBERT should have extracted some keywords
    assert len(data["extracted_keywords"]) > 0
