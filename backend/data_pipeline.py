import os
import gzip
import urllib.request
import bibtexparser
from database import get_db_connection, init_db

BIB_URL = "https://aclanthology.org/anthology+abstracts.bib.gz"
DATA_DIR = os.path.dirname(__file__)
BIB_FILE_GZ = os.path.join(DATA_DIR, "anthology+abstracts.bib.gz")
BIB_FILE = os.path.join(DATA_DIR, "anthology+abstracts.bib")

def decode_latex_accents(text):
    if not text: return text
    replacements = {
        '\\"a': 'ä', '\\"o': 'ö', '\\"u': 'ü', '\\"A': 'Ä', '\\"O': 'Ö', '\\"U': 'Ü',
        "\\'a": 'á', "\\'e": 'é', "\\'i": 'í', "\\'o": 'ó', "\\'u": 'ú',
        "\\'A": 'Á', "\\'E": 'É', "\\'I": 'Í', "\\'O": 'Ó', "\\'U": 'Ú',
        "\\`a": 'à', "\\`e": 'è', "\\`i": 'ì', "\\`o": 'ò', "\\`u": 'ù',
        "\\^a": 'â', "\\^e": 'ê', "\\^i": 'î', "\\^o": 'ô', "\\^u": 'û',
        "\\~a": 'ã', "\\~n": 'ñ', "\\~o": 'õ', "\\c c": 'ç', "\\'c": 'ć', 
        "\\'n": 'ń', "\\o": 'ø', "\\O": 'Ø', "\\ss": 'ß'
    }
    for latex, unicode_char in replacements.items():
        text = text.replace(latex, unicode_char)
    return text

def format_authors(author_str):
    if not author_str: return ''
    authors = author_str.split(' and ')
    formatted = []
    for author in authors:
        if ',' in author:
            parts = [p.strip() for p in author.split(',', 1)]
            formatted.append(f"{parts[1]} {parts[0]}")
        else:
            formatted.append(author.strip())
    return ', '.join(formatted)

def download_and_extract():
    if not os.path.exists(BIB_FILE):
        if not os.path.exists(BIB_FILE_GZ):
            print("Downloading ACL Anthology BibTeX...")
            urllib.request.urlretrieve(BIB_URL, BIB_FILE_GZ)
            print("Download complete.")
        
        print("Extracting BibTeX...")
        with gzip.open(BIB_FILE_GZ, 'rb') as f_in:
            with open(BIB_FILE, 'wb') as f_out:
                f_out.write(f_in.read())
        print("Extraction complete.")

def populate_db():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM papers")
    if cursor.fetchone()[0] > 0:
        print("Database already populated. Skipping download and parsing.")
        conn.close()
        return
        
    download_and_extract()
    import re
    print("Parsing BibTeX using memory-efficient streaming... This will be fast and reliable!")
    
    def entry_generator(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            current_entry = ""
            for line in f:
                if line.startswith('@'):
                    if current_entry:
                        yield current_entry
                    current_entry = line
                else:
                    current_entry += line
            if current_entry:
                yield current_entry

    # Regex to split an entry into key-value parts
    field_split_re = re.compile(r'\n\s*([a-zA-Z_]+)\s*=\s*')
    
    count = 0
    for raw_entry in entry_generator(BIB_FILE):
        raw_entry = raw_entry.strip()
        if not raw_entry:
            continue
            
        # The entry ends with a closing brace. Remove it to cleanly parse the last field.
        if raw_entry.endswith('}'):
            raw_entry = raw_entry[:-1]
            
        parts = field_split_re.split(raw_entry)
        
        entry_dict = {}
        # Following elements are alternating keys and values
        for i in range(1, len(parts) - 1, 2):
            key = parts[i].lower()
            val = parts[i+1].strip()
            
            # Remove trailing comma from the field
            if val.endswith(','):
                val = val[:-1].strip()
                
            # Remove bounding quotes or braces
            if val.startswith('{') and val.endswith('}'):
                val = val[1:-1].strip()
            elif val.startswith('"') and val.endswith('"'):
                val = val[1:-1].strip()
                
            # Remove LaTeX math mode formatting and text commands like \texttt{...}
            val = val.replace('$', '')
            val = re.sub(r'\\[a-zA-Z]+\s*\{', '{', val)
            
            # Clean all internal LaTeX braces and newlines
            val = val.replace('{', '').replace('}', '').replace('\n', ' ').strip()
            val = decode_latex_accents(val)
            entry_dict[key] = val
            
        year_str = entry_dict.get('year', '')
        if year_str.isdigit():
            y = int(year_str)
            if 2022 <= y <= 2026:
                t = entry_dict.get('title', '')
                if t:
                    a = entry_dict.get('abstract', '')
                    au = format_authors(entry_dict.get('author', ''))
                    u = entry_dict.get('url', '')
                    v = entry_dict.get('booktitle', entry_dict.get('journal', 'ACL Anthology'))
                    
                    cursor.execute('''
                        INSERT INTO papers (title, abstract, author, year, url, venue)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (t, a, au, str(y), u, v))
                    count += 1
                        
    conn.commit()
    conn.close()
    print(f"Inserted {count} papers into the database.")

if __name__ == "__main__":
    populate_db()
