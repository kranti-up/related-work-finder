import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "papers.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS papers USING fts5(
            title,
            abstract,
            author,
            year UNINDEXED,
            url UNINDEXED,
            venue UNINDEXED
        )
    ''')
    conn.commit()
    conn.close()

def search_papers(keywords: list, sort_by: str = "relevance"):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    clean_keywords = []
    for kw in keywords:
        # Sanitize keyword
        kw = kw.replace('"', '').replace("'", "")
        # Handle -, +, &, etc. by keeping them inside quotes for FTS5
        clean_keywords.append(f'"{kw}"')
        
    match_query = " OR ".join(clean_keywords)
    fts_query = f"title : ({match_query})"
    
    if sort_by == "year":
        query = '''
            SELECT title, abstract, author, year, url, venue, rank 
            FROM papers 
            WHERE papers MATCH ? 
            ORDER BY year DESC
            LIMIT 50
        '''
    else:
        query = '''
            SELECT title, abstract, author, year, url, venue, rank 
            FROM papers 
            WHERE papers MATCH ? 
            ORDER BY rank
            LIMIT 50
        '''
        
    try:
        cursor.execute(query, (fts_query,))
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()
