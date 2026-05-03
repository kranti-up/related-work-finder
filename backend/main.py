from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import threading

from database import search_papers
from nlp_utils import get_keywords_from_abstract
from fastapi.staticfiles import StaticFiles
import data_pipeline

app = FastAPI()

frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run data pipeline on startup in a separate thread
@app.on_event("startup")
def startup_event():
    print("Running data pipeline check on startup...")
    threading.Thread(target=data_pipeline.populate_db).start()

class SearchRequest(BaseModel):
    query: str
    query_type: str # "keywords" or "abstract"
    sort_by: Optional[str] = "relevance"

# API routes (defined before static mount)
@app.post("/api/search")
def search(request: SearchRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    keywords_to_search = []
    extracted_keywords = []
    
    if request.query_type == "abstract":
        # Extract keywords using KeyBERT
        extracted_keywords = get_keywords_from_abstract(query, top_n=8)
        keywords_to_search = extracted_keywords
    else:
        # Split keywords by comma or space
        if "," in query:
            keywords_to_search = [k.strip() for k in query.split(",") if k.strip()]
        else:
            keywords_to_search = [k.strip() for k in query.split() if k.strip()]
            
    if not keywords_to_search:
        raise HTTPException(status_code=400, detail="No valid keywords found")
        
    results = search_papers(keywords_to_search, sort_by=request.sort_by)
    
    return {
        "results": results,
        "extracted_keywords": extracted_keywords if request.query_type == "abstract" else []
    }

# Serve static files from the root last
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

@app.get("/debug")
def debug_clembench():
    import re
    bib_file = os.path.join(os.path.dirname(__file__), "anthology.bib")
    if not os.path.exists(bib_file):
        return {"error": "file not found"}
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()
    entries = re.split(r'\n@', content)
    for entry in entries:
        if "clembench: Using Game Play" in entry:
            # Let's see what our regex parser does
            field_split_re = re.compile(r'\n\s*([a-zA-Z_]+)\s*=\s*')
            raw = entry.strip()
            if raw.endswith('}'): raw = raw[:-1]
            parts = field_split_re.split(raw)
            parsed_keys = [parts[i].lower() for i in range(1, len(parts)-1, 2)]
            
            return {
                "raw_entry": entry,
                "parsed_keys": parsed_keys,
                "abstract_val": parts[parsed_keys.index('abstract')*2 + 2] if 'abstract' in parsed_keys else "NO ABSTRACT KEY FOUND"
            }
    return {"error": "entry not found"}
