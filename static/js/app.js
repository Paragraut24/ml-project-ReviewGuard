// ReviewGuard - Forensic Precision JavaScript

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeButton(newTheme);
}

function updateThemeButton(theme) {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;
    
    if (theme === 'light') {
        btn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
            <span>Dark</span>
        `;
    } else {
        btn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="5"/>
                <line x1="12" y1="1" x2="12" y2="3"/>
                <line x1="12" y1="21" x2="12" y2="23"/>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                <line x1="1" y1="12" x2="3" y2="12"/>
                <line x1="21" y1="12" x2="23" y2="12"/>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
            </svg>
            <span>Light</span>
        `;
    }
}

// Star Rating Management
window.selectedRating = null;

function initStarRating() {
    const stars = document.querySelectorAll('.star');
    const ratingText = document.getElementById('starRatingText');
    
    stars.forEach((star) => {
        const rating = parseInt(star.dataset.rating);
        
        star.addEventListener('click', () => {
            if (window.selectedRating === rating) {
                // Deselect
                window.selectedRating = null;
                updateStars(0);
                ratingText.textContent = 'Not provided';
            } else {
                // Select
                window.selectedRating = rating;
                updateStars(rating);
                ratingText.textContent = rating + ' / 5';
            }
        });
        
        star.addEventListener('mouseenter', () => {
            updateStars(rating, true);
        });
        
        star.addEventListener('mouseleave', () => {
            updateStars(window.selectedRating || 0, false);
        });
    });
}

function updateStars(rating, isHover = false) {
    const stars = document.querySelectorAll('.star');
    stars.forEach((star) => {
        const starRating = parseInt(star.dataset.rating);
        star.classList.remove('active', 'hover-preview');
        
        if (starRating <= rating) {
            if (isHover && starRating > (window.selectedRating || 0)) {
                star.classList.add('hover-preview');
            } else {
                star.classList.add('active');
            }
        }
    });
}

// Demo Review Samples
const demoReviews = {
    fake1: {
        text: "AMAZING!!! Best product EVER!!! Love love love!!! Buy NOW!!!",
        rating: 5
    },
    genuine: {
        text: "Battery lasts about 6 hours with moderate use. The charging port feels slightly loose but it still works fine after 3 weeks.",
        rating: 3
    },
    unverifiable: {
        text: "This is a great tool to determine if the problem is a bad charger, or a bad battery",
        rating: 4
    },
    fake2: {
        text: "I loved this product, it is too good. bought one for myself, bought one for my brother, bought one for my sister. then all enjoyed it and loved it. such an amazing product.",
        rating: 5
    }
};

function loadDemo(key) {
    const demo = demoReviews[key];
    if (!demo) return;
    
    // Set textarea
    document.getElementById('reviewInput').value = demo.text;
    
    // Set star rating
    window.selectedRating = demo.rating;
    updateStars(demo.rating);
    document.getElementById('starRatingText').textContent = demo.rating + ' / 5';
}

// Analysis Function with 1-second delay
async function analyzeReview() {
    const review = document.getElementById('reviewInput').value.trim();
    if (!review) {
        alert('Please enter a review to analyze');
        return;
    }
    
    const selectedRating = window.selectedRating || null;
    const btn = document.getElementById('analyzeBtn');
    const resultCard = document.getElementById('resultCard');
    
    // Show loading state
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner"></div><span>Processing...</span>';
    
    // Show loading steps
    showLoadingSteps();
    
    try {
        const payload = { review };
        if (selectedRating !== null) {
            payload.rating = selectedRating;
        }
        
        // Make API call
        const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        let data = {};
        try { 
            data = await res.json(); 
        } catch (_) {
            throw new Error('Invalid response from server');
        }
        
        if (!res.ok || data.error) {
            throw new Error(data.error || 'Analysis failed. Please try again.');
        }
        
        // Add 1-second delay to show loading animation
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        hideLoadingSteps();
        showResult(data);
        
    } catch (e) {
        hideLoadingSteps();
        showError(e.message || 'Analysis failed. Please try again.');
    }
    
    // Reset button
    btn.disabled = false;
    btn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
        </svg>
        <span>Execute Trace</span>
    `;
}

// Loading Steps Animation
function showLoadingSteps() {
    const resultCard = document.getElementById('resultCard');
    resultCard.innerHTML = `
        <div class="card">
            <div class="card-header">
                <div class="card-title">Processing</div>
                <div class="card-badge">In Progress</div>
            </div>
            <div class="loading-steps">
                <div class="loading-step" id="loadingStep">Initializing forensic scan...</div>
            </div>
        </div>
    `;
    resultCard.classList.add('show');
    
    const steps = [
        'Initializing forensic scan...',
        'Running BERT semantic analysis...',
        'Executing GNN behavioral mapping...',
        'Applying heuristic detection rules...',
        'Generating verdict...'
    ];
    
    let currentStep = 0;
    window.loadingInterval = setInterval(() => {
        currentStep = (currentStep + 1) % steps.length;
        const stepEl = document.getElementById('loadingStep');
        if (stepEl) {
            stepEl.textContent = steps[currentStep];
        }
    }, 600);
}

function hideLoadingSteps() {
    if (window.loadingInterval) {
        clearInterval(window.loadingInterval);
    }
}

// Show Error Function
function showError(message) {
    const card = document.getElementById('resultCard');
    card.innerHTML = `
        <div class="card">
            <div class="card-header">
                <div class="card-title">Error</div>
                <div class="card-badge" style="background: rgba(186, 26, 26, 0.1); border-color: var(--error); color: var(--error);">Failed</div>
            </div>
            <div class="card-body" style="text-align: center; padding: 40px 24px;">
                <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px; color: var(--error);">
                    Analysis Failed
                </div>
                <div style="color: var(--on-surface-variant); font-size: 13px;">
                    ${message}
                </div>
            </div>
        </div>
    `;
    card.classList.add('show');
}

// Show Result Function
function showResult(data) {
    const card = document.getElementById('resultCard');
    const verdict = String(data.verdict || '').trim().toUpperCase();
    const isFake = verdict === 'FAKE';
    const isUnv = verdict === 'UNVERIFIABLE';
    
    // Build verdict badge
    let verdictClass = isFake ? 'verdict-fake' : isUnv ? 'verdict-unverifiable' : 'verdict-genuine';
    let verdictTitle = isFake ? 'FAKE' : isUnv ? 'UNVERIFIABLE' : 'GENUINE';
    let verdictSubtitle = isUnv ? 'Models disagree — manual review required' : '';
    
    // Build metrics
    const metricsHTML = `
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Confidence</div>
                <div class="metric-value">${data.confidence}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">BERT</div>
                <div class="metric-value">${data.bert_score}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">GNN</div>
                <div class="metric-value">${data.gnn_score}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Heuristic</div>
                <div class="metric-value">${data.heuristic_score}%</div>
            </div>
        </div>
    `;
    
    // Build divergence bar
    const divergence = data.divergence || 0;
    const agreement = (1 - divergence) * 100;
    const barColor = agreement > 70 ? 'var(--primary-container)' : '#f59e0b';
    const divergenceHTML = `
        <div class="progress-bar-container">
            <div class="progress-bar-label">
                <span>Model Agreement</span>
                <span class="mono-data">${agreement.toFixed(1)}%</span>
            </div>
            <div class="progress-bar-track">
                <div class="progress-bar-fill" style="width: ${agreement}%; background: ${barColor};"></div>
            </div>
            <div class="progress-bar-text">
                Divergence: ${divergence.toFixed(3)} ${divergence >= 0.35 ? '(High divergence → UNVERIFIABLE)' : ''}
            </div>
        </div>
    `;
    
    // Build signals
    const reasons = Array.isArray(data.reasons) && data.reasons.length ? data.reasons : ['No explanation available.'];
    const signalsTitle = isFake ? 'Active Signal Triggers' : isUnv ? 'Conflict Summary' : 'Authenticity Signals';
    
    let signalsHTML = reasons.map((r, i) => 
        `<span class="signal-tag" style="animation-delay: ${i * 0.05}s">${r}</span>`
    ).join('');
    
    // Add submitted rating
    if (data.submitted_rating !== null && data.submitted_rating !== undefined) {
        signalsHTML += `<span class="signal-tag" style="animation-delay: ${reasons.length * 0.05}s">Rating: ${data.submitted_rating}/5</span>`;
    } else {
        signalsHTML += `<span class="signal-tag" style="animation-delay: ${reasons.length * 0.05}s">No rating provided</span>`;
    }
    
    // Build complete result HTML
    card.innerHTML = `
        <div class="card">
            <div class="verdict-badge ${verdictClass}">
                <div class="verdict-label">Verdict Status</div>
                <div class="verdict-title">${verdictTitle}</div>
                ${verdictSubtitle ? `<div style="font-size: 12px; color: var(--on-surface-variant); margin-top: 8px;">${verdictSubtitle}</div>` : ''}
                <div class="confidence-score">${data.confidence}% Confidence</div>
            </div>
            
            ${metricsHTML}
            ${divergenceHTML}
            
            <div class="signals-section">
                <div class="signals-title">${signalsTitle}</div>
                <div>${signalsHTML}</div>
            </div>
        </div>
    `;
    
    card.classList.add('show');
}

// Initialize Everything
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initStarRating();
});
