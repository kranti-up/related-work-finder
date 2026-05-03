from keybert import KeyBERT

# Initialize KeyBERT model lazily
kw_model = None

def get_keywords_from_abstract(abstract: str, top_n: int = 5):
    global kw_model
    if kw_model is None:
        kw_model = KeyBERT()
    
    # Extract keywords
    # KeyBERT returns a list of tuples: [('keyword', score), ...]
    keywords = kw_model.extract_keywords(abstract, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=top_n)
    
    return [kw[0] for kw in keywords]
