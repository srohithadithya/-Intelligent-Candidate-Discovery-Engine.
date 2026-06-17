let allCandidates = [];

document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('candidates-grid');
    const expFilter = document.getElementById('exp-filter');
    const skillSearch = document.getElementById('skill-search');

    // Fetch the generated showcase data
    fetch('showcase_data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            allCandidates = data;
            renderCandidates(allCandidates);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            grid.innerHTML = `<div class="loading" style="color: #ef4444;">Error loading candidate data. Make sure you run python build_showcase_data.py first!</div>`;
        });

    // Event Listeners for Filters
    expFilter.addEventListener('change', applyFilters);
    skillSearch.addEventListener('input', applyFilters);
});

function applyFilters() {
    const expValue = document.getElementById('exp-filter').value;
    const skillValue = document.getElementById('skill-search').value.toLowerCase();

    let filtered = allCandidates.filter(candidate => {
        // Experience Filter
        let expMatch = true;
        const years = candidate.years_of_experience || 0;
        if (expValue === 'fresher' && years > 2) expMatch = false;
        if (expValue === 'mid' && (years < 3 || years > 7)) expMatch = false;
        if (expValue === 'senior' && years < 8) expMatch = false;

        // Skill Filter
        let skillMatch = true;
        if (skillValue) {
            const skillsStr = (candidate.skills || []).join(' ').toLowerCase();
            if (!skillsStr.includes(skillValue)) skillMatch = false;
        }

        return expMatch && skillMatch;
    });

    renderCandidates(filtered);
}

function renderCandidates(candidates) {
    const grid = document.getElementById('candidates-grid');
    grid.innerHTML = ''; // Clear current
    
    if (candidates.length === 0) {
        grid.innerHTML = '<div class="loading" style="color:var(--text-muted)">No candidates match your current filters.</div>';
        return;
    }

    candidates.forEach((candidate, index) => {
        // Add a staggered entrance animation delay, cap at 1s to prevent huge delays on reset
        const delay = Math.min(index * 0.05, 1);
        const card = createCandidateCard(candidate, delay);
        grid.appendChild(card);
    });
}

function createCandidateCard(candidate, delay) {
    const card = document.createElement('div');
    card.className = 'candidate-card';
    card.style.animation = `fadeUp 0.6s ease forwards ${delay}s`;
    card.style.opacity = '0'; // Starts hidden for animation

    // Format score
    const scoreFormatted = parseFloat(candidate.score).toFixed(4);

    // Build skills HTML
    const skillsHtml = candidate.skills && candidate.skills.length > 0 
        ? candidate.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')
        : '<span class="skill-tag">No skills listed</span>';

    card.innerHTML = `
        <div class="card-header">
            <div class="rank-badge">#${candidate.rank}</div>
            <div class="score-badge">Score: ${scoreFormatted}</div>
        </div>
        
        <div class="card-title">
            <h3>${candidate.name}</h3>
            <p>${candidate.headline || candidate.current_company || 'Candidate'}</p>
        </div>

        <div class="card-meta">
            <div class="meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                ${candidate.location || 'Unknown'}
            </div>
            <div class="meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                ${candidate.years_of_experience} Years Exp
            </div>
        </div>

        <div class="card-skills">
            ${skillsHtml}
        </div>

        <div class="card-reasoning">
            <strong>AI Match Reasoning</strong>
            ${candidate.reasoning}
        </div>
    `;

    return card;
}

// Add animation keyframes dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
