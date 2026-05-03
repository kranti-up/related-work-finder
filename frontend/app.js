document.addEventListener('DOMContentLoaded', () => {
    const searchTypeBtns = document.querySelectorAll('.toggle-btn');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const sortSelect = document.getElementById('sort-select');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.querySelector('.spinner');
    
    const resultsContainer = document.getElementById('results-container');
    const extractedKeywordsDiv = document.getElementById('extracted-keywords');
    const tagsContainer = document.querySelector('.tags');
    const resultsCount = document.getElementById('results-count');
    const papersList = document.getElementById('papers-list');
    
    let currentSearchType = 'keywords';

    // Toggle search type
    searchTypeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            searchTypeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentSearchType = btn.dataset.type;
            
            if (currentSearchType === 'keywords') {
                searchInput.placeholder = "Enter keywords (e.g., transformer, attention) or paste an abstract...";
            } else {
                searchInput.placeholder = "Paste an abstract here to extract keywords and search...";
            }
        });
    });

    // Handle search
    const performSearch = async () => {
        const query = searchInput.value.trim();
        if (!query) return;

        // UI Loading state
        searchBtn.disabled = true;
        btnText.classList.add('hidden');
        spinner.classList.remove('hidden');
        resultsContainer.classList.add('hidden');
        
        try {
            const response = await fetch('http://127.0.0.1:8000/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    query_type: currentSearchType,
                    sort_by: sortSelect.value
                })
            });

            if (!response.ok) {
                throw new Error('Search failed');
            }

            const data = await response.json();
            renderResults(data);
            
        } catch (error) {
            console.error('Error during search:', error);
            alert('An error occurred during search. Please try again.');
        } finally {
            // Restore UI
            searchBtn.disabled = false;
            btnText.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    };

    searchBtn.addEventListener('click', performSearch);
    
    // Sort change re-triggers search if there's a query
    sortSelect.addEventListener('change', () => {
        if (searchInput.value.trim() && !resultsContainer.classList.contains('hidden')) {
            performSearch();
        }
    });

    function renderResults(data) {
        resultsContainer.classList.remove('hidden');
        
        // Handle Extracted Keywords
        if (data.extracted_keywords && data.extracted_keywords.length > 0) {
            extractedKeywordsDiv.classList.remove('hidden');
            tagsContainer.innerHTML = data.extracted_keywords
                .map(kw => `<span class="tag">${kw}</span>`)
                .join('');
        } else {
            extractedKeywordsDiv.classList.add('hidden');
        }

        // Render papers
        resultsCount.textContent = `${data.results.length} papers found`;
        
        if (data.results.length === 0) {
            papersList.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 2rem;">No relevant papers found in the ACL Anthology (2022-2026).</p>';
            return;
        }

        papersList.innerHTML = data.results.map(paper => `
            <div class="paper-card">
                <a href="${paper.url || '#'}" target="_blank" class="paper-title">${paper.title}</a>
                <div class="paper-meta">
                    <span class="venue"><strong>Venue:</strong>&nbsp;${paper.venue}</span>
                    <span class="year"><strong>Year:</strong>&nbsp;${paper.year}</span>
                    <span class="author"><strong>Authors:</strong>&nbsp;${paper.author}</span>
                </div>
                <div class="paper-abstract">
                    ${paper.abstract ? paper.abstract.substring(0, 300) + '...' : 'No abstract available.'}
                </div>
            </div>
        `).join('');
    }
});
