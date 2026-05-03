---
title: Related Work Finder
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: cc-by-nc-4.0
---
# Related Work Finder

**Live Demo**: 

A search engine designed to help researchers find relevant computer science and AI papers from the ACL Anthology. 

## Current Features

- **Keyword Search**: Full-text search using SQLite's FTS5 engine, with support for boolean logic and special characters.
- **Abstract Search**: Uses the KeyBERT NLP transformer to extract keywords from user-provided abstracts and runs a targeted search.
- **Dataset Parsing**: Automatically downloads the `anthology+abstracts.bib.gz` dataset from ACL servers on startup and parses the BibTeX data (filtered for years 2022–2026).
- **Web Interface**: A responsive UI displaying paper titles, authors, venues, years, and abstracts. Results can be sorted by relevance or year.
- **Deployment**: Includes a `pytest` suite running via GitHub Actions, and a `Dockerfile` configured for deployment to Hugging Face Spaces.

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python 3.10, FastAPI, Uvicorn
- **Database**: SQLite (FTS5 Virtual Tables)
- **NLP**: KeyBERT

## Local Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
3. Open your web browser and navigate to:
   `http://127.0.0.1:8000/frontend/index.html`

## Planned for Phase 2

- **Fuzzy Searching**: Implement robust typo-tolerance and spelling correction (e.g. using `pyspellchecker` or trigram matching) to handle slight misspellings in search queries.
- **Semantic Scholar Integration**: Pull citation counts and sort papers by impact/citations instead of just basic relevance.
- **Advanced PDF Parsing**: Extract text and insights directly from full paper PDFs or images instead of just using abstracts.
