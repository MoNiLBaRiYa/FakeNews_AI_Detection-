// Professional Fake News Detector - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const articleInput = document.getElementById('articleInput');
    const charCount = document.getElementById('charCount');
    const charHint = document.getElementById('charHint');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsCard = document.getElementById('resultsCard');
    const resultsContent = document.getElementById('resultsContent');
    const newsGrid = document.getElementById('newsGrid');
    const newsQuery = document.getElementById('newsQuery');
    const loadingOverlay = document.getElementById('loadingOverlay');

    // Character counter
    articleInput.addEventListener('input', function() {
        const count = this.value.length;
        charCount.textContent = count;
        
        if (count < 100) {
            charHint.textContent = `• ${100 - count} more characters recommended`;
            charHint.classList.remove('text-green-500');
            charHint.classList.add('text-yellow-500');
            analyzeBtn.disabled = count < 10;
        } else {
            charHint.textContent = '• Ready for analysis';
            charHint.classList.remove('text-yellow-500');
            charHint.classList.add('text-green-500');
            analyzeBtn.disabled = false;
        }
    });

    // Auto-resize textarea
    articleInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
});

// Analyze Article
function analyzeArticle() {
    const articleInput = document.getElementById('articleInput');
    const text = articleInput.value.trim();
    
    if (!text) {
        showToast('Please enter some text to analyze', 'warning');
        return;
    }
    
    if (text.length < 10) {
        showToast('Please enter at least 10 characters', 'warning');
        return;
    }
    
    if (text.length < 100) {
        showToast('For best results, please provide at least 100 characters', 'info');
    }
    
    // Show loading
    showLoading();
    
    // Send to backend
    fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text })
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .then(data => {
        hideLoading();
        
        if (data.error) {
            showToast(data.error, 'error');
            return;
        }
        
        displayResults(data);
        showToast('Analysis complete!', 'success');
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showToast('Analysis failed. Please try again.', 'error');
    });
}

// Display Results
function displayResults(data) {
    const resultsCard = document.getElementById('resultsCard');
    const resultsContent = document.getElementById('resultsContent');
    
    const isFake = data.prediction_en === 'Fake News';
    const confidence = data.confidence || 0;
    const reliability = data.reliability || 'Unknown';
    const language = data.language_name || 'English';
    
    const resultHTML = `
        <div class="inline-flex items-center gap-3 px-6 py-4 rounded-2xl text-xl font-bold mb-6 ${isFake ? 'bg-gradient-to-r from-red-50 to-red-100 text-red-600 border-2 border-red-500' : 'bg-gradient-to-r from-green-50 to-green-100 text-green-600 border-2 border-green-500'} animate-[badgePop_0.5s_cubic-bezier(0.68,-0.55,0.265,1.55)]">
            <i class="fas fa-${isFake ? 'exclamation-triangle' : 'check-circle'} text-2xl"></i>
            <span>${data.prediction}</span>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div class="bg-gray-50 p-6 rounded-2xl border-2 border-gray-200 transition-all duration-300 hover:border-blue-500 hover:-translate-y-1 hover:shadow-lg">
                <div class="text-sm font-semibold text-gray-600 mb-2">Confidence Score</div>
                <div class="text-3xl font-black text-gray-900">${confidence}%</div>
                <div class="w-full h-3 bg-gray-200 rounded-full overflow-hidden mt-4">
                    <div class="h-full bg-gradient-to-r from-green-500 to-blue-500 rounded-full transition-all duration-1000 ease-out relative overflow-hidden" style="width: ${confidence}%;">
                        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-[shimmer_2s_infinite]"></div>
                    </div>
                </div>
            </div>
            
            <div class="bg-gray-50 p-6 rounded-2xl border-2 border-gray-200 transition-all duration-300 hover:border-purple-500 hover:-translate-y-1 hover:shadow-lg">
                <div class="text-sm font-semibold text-gray-600 mb-2">Reliability Rating</div>
                <div class="text-3xl font-black text-gray-900">${reliability}</div>
                <div class="mt-2 text-2xl">
                    ${getReliabilityStars(reliability)}
                </div>
            </div>
            
            <div class="bg-gray-50 p-6 rounded-2xl border-2 border-gray-200 transition-all duration-300 hover:border-pink-500 hover:-translate-y-1 hover:shadow-lg">
                <div class="text-sm font-semibold text-gray-600 mb-2">Detected Language</div>
                <div class="text-3xl font-black text-gray-900">${language}</div>
                <div class="mt-2 text-sm text-gray-600">
                    <i class="fas fa-language"></i> Auto-detected
                </div>
            </div>
        </div>
        
        <div class="mt-8 p-6 bg-${isFake ? 'red' : 'green'}-50 rounded-2xl border-l-4 border-${isFake ? 'red' : 'green'}-500">
            <h4 class="text-base font-bold text-gray-900 mb-3 flex items-center gap-2">
                <i class="fas fa-info-circle text-${isFake ? 'red' : 'green'}-500"></i> Analysis Summary
            </h4>
            <p class="text-sm text-gray-700 leading-relaxed">
                ${isFake 
                    ? 'Our AI has detected patterns commonly associated with misinformation. Please verify this content with trusted sources before sharing.'
                    : 'This content appears to be authentic based on our analysis. However, always cross-reference important information with multiple reliable sources.'
                }
            </p>
        </div>
    `;
    
    resultsContent.innerHTML = resultHTML;
    resultsCard.classList.remove('hidden');
    
    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Get Reliability Stars
function getReliabilityStars(reliability) {
    const stars = {
        'High': '⭐⭐⭐⭐⭐',
        'Medium': '⭐⭐⭐',
        'Low': '⭐'
    };
    return `<span style="font-size: 1.25rem;">${stars[reliability] || '⭐⭐⭐'}</span>`;
}

// Clear Results
function clearResults() {
    const resultsCard = document.getElementById('resultsCard');
    resultsCard.classList.add('hidden');
    document.getElementById('articleInput').value = '';
    document.getElementById('charCount').textContent = '0';
    const charHint = document.getElementById('charHint');
    charHint.textContent = '• Minimum 100 recommended';
    charHint.classList.remove('text-green-500', 'text-yellow-500');
    charHint.classList.add('text-gray-400');
    document.getElementById('analyzeBtn').disabled = true;
}

// Search News
function searchNews() {
    const query = document.getElementById('newsQuery').value.trim() || 'latest';
    const newsGrid = document.getElementById('newsGrid');
    
    if (!query) {
        showToast('Please enter a search topic', 'warning');
        return;
    }
    
    // Show loading
    newsGrid.innerHTML = `
        <div class="col-span-full text-center py-12">
            <div class="w-16 h-16 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
            <p class="text-gray-600 font-semibold">Fetching and analyzing news...</p>
        </div>
    `;
    
    fetch(`/fetch_news?query=${encodeURIComponent(query)}`)
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (data.error) {
            newsGrid.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <i class="fas fa-exclamation-circle text-5xl text-red-500 mb-4"></i>
                    <p class="text-gray-600 font-semibold">${data.error}</p>
                </div>
            `;
            return;
        }
        
        if (!data.news || data.news.length === 0) {
            newsGrid.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <i class="fas fa-search text-5xl text-gray-400 mb-4"></i>
                    <p class="text-gray-600 font-semibold">No news found for "${query}". Try a different search term.</p>
                </div>
            `;
            return;
        }
        
        displayNewsCards(data.news, data.predictions);
        showToast(`Found ${data.news.length} articles`, 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        newsGrid.innerHTML = `
            <div class="col-span-full text-center py-12">
                <i class="fas fa-exclamation-triangle text-5xl text-red-500 mb-4"></i>
                <p class="text-gray-600 font-semibold">Failed to fetch news. Please try again.</p>
            </div>
        `;
        showToast('Failed to fetch news', 'error');
    });
}

// Display News Cards
function displayNewsCards(news, predictions) {
    const newsGrid = document.getElementById('newsGrid');
    newsGrid.innerHTML = '';
    
    news.forEach((article, index) => {
        const prediction = predictions[index];
        const isFake = prediction === 'Fake News';
        
        const card = document.createElement('div');
        card.className = 'bg-gray-50 border-2 border-gray-200 rounded-2xl p-6 transition-all duration-300 cursor-pointer hover:border-blue-500 hover:-translate-y-1 hover:shadow-xl animate-[cardFadeIn_0.5s_ease-out]';
        card.innerHTML = `
            <div class="flex justify-between items-start mb-4">
                <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-700 text-white rounded-xl flex items-center justify-center font-bold text-lg">
                    ${index + 1}
                </div>
                <div class="px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wide ${isFake ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}">
                    <i class="fas fa-${isFake ? 'times-circle' : 'check-circle'}"></i>
                    ${isFake ? 'Fake' : 'Real'}
                </div>
            </div>
            <div class="text-gray-900 text-sm leading-relaxed font-medium">${article}</div>
        `;
        
        card.addEventListener('click', () => {
            document.getElementById('articleInput').value = article;
            document.getElementById('articleInput').dispatchEvent(new Event('input'));
            window.scrollTo({ top: 0, behavior: 'smooth' });
            showToast('Article copied to analyzer', 'info');
        });
        
        newsGrid.appendChild(card);
    });
}

// Show/Hide Loading
function showLoading() {
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    
    const colors = {
        success: 'bg-white border-l-4 border-green-500',
        error: 'bg-white border-l-4 border-red-500',
        warning: 'bg-white border-l-4 border-yellow-500',
        info: 'bg-white border-l-4 border-blue-500'
    };
    
    const iconColors = {
        success: 'text-green-500',
        error: 'text-red-500',
        warning: 'text-yellow-500',
        info: 'text-blue-500'
    };
    
    toast.className = `${colors[type]} px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-4 min-w-[300px] transform translate-x-[500px] transition-transform duration-500`;
    toast.innerHTML = `
        <i class="fas fa-${icons[type]} text-xl ${iconColors[type]}"></i>
        <span class="flex-1 text-sm font-semibold text-gray-900">${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => toast.style.transform = 'translateX(0)', 10);
    setTimeout(() => {
        toast.style.transform = 'translateX(500px)';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

// Help Modal
function showHelp() {
    document.getElementById('helpModal').classList.remove('hidden');
}

function closeHelp() {
    document.getElementById('helpModal').classList.add('hidden');
}

// Close modal on outside click
document.getElementById('helpModal')?.addEventListener('click', function(e) {
    if (e.target === this) {
        closeHelp();
    }
});

// Logout
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        fetch('/logout', { method: 'POST' })
            .then(() => {
                showToast('Logged out successfully', 'success');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            })
            .catch(() => {
                window.location.href = '/';
            });
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to analyze
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const articleInput = document.getElementById('articleInput');
        if (document.activeElement === articleInput && articleInput.value.trim()) {
            analyzeArticle();
        }
    }
    
    // Escape to close modal
    if (e.key === 'Escape') {
        closeHelp();
    }
});

// Initialize
console.log('%c🛡️ TruthGuard Initialized', 'font-size: 20px; color: #3b82f6; font-weight: bold;');
console.log('%cAI-Powered Fake News Detection System', 'font-size: 14px; color: #64748b;');
console.log('%c✓ 99.63% Accuracy', 'color: #10b981;');
console.log('%c✓ Multi-Language Support', 'color: #10b981;');
console.log('%c✓ Real-Time Analysis', 'color: #10b981;');
