import argparse
import json
import gzip
import csv
import math
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import sys

JD_TEXT = """
Senior AI Engineer — Founding Team
Deep technical depth in modern ML systems — embeddings, retrieval, ranking, LLMs, fine-tuning.
Scrappy product-engineering attitude
own the intelligence layer of Redrob's product. ranking, retrieval, and matching systems
embeddings, hybrid retrieval, and LLM-based re-ranking
evaluation infrastructure — offline benchmarks, online A/B testing, recruiter-feedback loops
applied ML/AI roles at product companies (not pure services).
shipped at least one end-to-end ranking, search, or recommendation system to real users at meaningful scale.
opinions about retrieval (hybrid vs dense), evaluation (offline vs online), and LLM integration
Production experience with embeddings-based retrieval systems (sentence-transformers, OpenAI embeddings, BGE, E5) deployed to real users.
Production experience with vector databases or hybrid search infrastructure — Pinecone, Weaviate, Qdrant, Milvus, OpenSearch, Elasticsearch, FAISS
Strong Python.
evaluation frameworks for ranking systems — NDCG, MRR, MAP
LLM fine-tuning experience (LoRA, QLoRA, PEFT)
learning-to-rank models (XGBoost-based or neural)
"""

def is_honeypot(candidate):
    # 1. Expert skill with 0 duration
    for skill in candidate.get('skills', []):
        if skill.get('proficiency') == 'expert' and skill.get('duration_months', 0) == 0:
            return True
            
    # 2. Job duration longer than possible total experience + 1 year buffer
    total_exp_months = candidate.get('profile', {}).get('years_of_experience', 0) * 12
    for job in candidate.get('career_history', []):
        if job.get('duration_months', 0) > (total_exp_months + 12):
            return True
            
    # 3. Education start > end
    for edu in candidate.get('education', []):
        if edu.get('start_year', 0) > edu.get('end_year', 9999):
            return True
            
    return False

def extract_text(candidate):
    parts = []
    profile = candidate.get('profile', {})
    parts.append(profile.get('headline', ''))
    parts.append(profile.get('summary', ''))
    
    for job in candidate.get('career_history', []):
        parts.append(job.get('title', ''))
        parts.append(job.get('description', ''))
        
    for skill in candidate.get('skills', []):
        parts.append(skill.get('name', ''))
        
    return ' '.join(parts).lower()

def calculate_heuristics(candidate):
    profile = candidate.get('profile', {})
    history = candidate.get('career_history', [])
    signals = candidate.get('redrob_signals', {})
    
    score_multiplier = 1.0
    
    # Experience
    yoe = profile.get('years_of_experience', 0)
    if 5 <= yoe <= 9:
        score_multiplier *= 1.2
    elif yoe < 4 or yoe > 12:
        score_multiplier *= 0.5
        
    # Consulting check
    consulting_firms = ['tcs', 'infosys', 'wipro', 'accenture', 'cognizant', 'capgemini']
    all_consulting = True
    if history:
        for job in history:
            company_lower = job.get('company', '').lower()
            if not any(firm in company_lower for firm in consulting_firms):
                all_consulting = False
                break
    else:
        all_consulting = False
        
    if all_consulting and history:
        score_multiplier *= 0.1 # Heavy penalty
        
    # Title chasers
    if len(history) > 3:
        durations = [job.get('duration_months', 0) for job in history if job.get('duration_months')]
        if durations and sum(durations)/len(durations) < 18:
            score_multiplier *= 0.7 # Penalty
            
    # Behavioral Signals
    last_active = signals.get('last_active_date', '')
    if last_active:
        try:
            last_date = datetime.strptime(last_active, '%Y-%m-%d')
            current = datetime(2026, 6, 17) # reference date
            if (current - last_date).days > 180:
                score_multiplier *= 0.5
        except:
            pass
            
    response_rate = signals.get('recruiter_response_rate', 1.0)
    if response_rate < 0.10:
        score_multiplier *= 0.4
        
    github_score = signals.get('github_activity_score', -1)
    if github_score > 0:
        score_multiplier *= 1.1
        
    # Positive signals from titles
    good_titles = ['ai engineer', 'machine learning', 'data scientist', 'backend', 'software engineer', 'nlp engineer']
    bad_titles = ['marketing', 'hr', 'accountant', 'customer support', 'operations', 'sales', 'business analyst']
    
    current_title = profile.get('current_title', '').lower()
    if any(t in current_title for t in good_titles):
        score_multiplier *= 1.3
    if any(t in current_title for t in bad_titles):
        score_multiplier *= 0.2
        
    # Pure research check
    if profile.get('current_industry', '').lower() == 'research':
        score_multiplier *= 0.5
        
    return score_multiplier

def generate_reasoning(candidate, tfidf_score, heuristic_multiplier):
    profile = candidate.get('profile', {})
    yoe = profile.get('years_of_experience', 0)
    title = profile.get('current_title', 'Professional')
    
    skills = [s.get('name', '') for s in candidate.get('skills', [])]
    relevant_skills = [s for s in skills if s.lower() in ['python', 'embedding', 'vector', 'retrieval', 'ranking', 'search', 'recommendation', 'llm', 'machine learning', 'nlp']]
    
    reasons = []
    reasons.append(f"Candidate is a {title} with {yoe} years of experience.")
    
    if relevant_skills:
        reasons.append(f"Has relevant skills including {', '.join(relevant_skills[:3])}.")
    
    # Check gaps
    signals = candidate.get('redrob_signals', {})
    notice_period = signals.get('notice_period_days', 0)
    if notice_period > 30:
        reasons.append(f"Note: Notice period is {notice_period} days (over the preferred 30 days).")
        
    last_active = signals.get('last_active_date', '')
    if last_active:
        try:
            last_date = datetime.strptime(last_active, '%Y-%m-%d')
            current = datetime(2026, 6, 17)
            days_inactive = (current - last_date).days
            if days_inactive > 180:
                reasons.append(f"Concern: Has not been active on platform for {days_inactive} days.")
        except:
            pass
            
    if tfidf_score > 0.05:
        reasons.append("Strong semantic match with the JD's focus on retrieval and ranking systems.")
        
    if heuristic_multiplier < 0.5:
        reasons.append("However, candidate has consulting-only background or irrelevant primary roles.")
        
    return " ".join(reasons)

def main():
    parser = argparse.ArgumentParser(description="Rank candidates based on JD")
    parser.add_argument('--candidates', required=True, help="Path to candidates.jsonl or candidates.jsonl.gz")
    parser.add_argument('--out', required=True, help="Path to output CSV")
    args = parser.parse_args()

    print(f"[{datetime.now()}] Starting candidate processing...")
    
    candidates = []
    is_gz = args.candidates.endswith('.gz')
    open_func = gzip.open if is_gz else open
    mode = 'rt' if is_gz else 'r'
    
    # Pass 1: Filter and Extract
    filtered_count = 0
    with open_func(args.candidates, mode, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            cand = json.loads(line)
            if is_honeypot(cand):
                filtered_count += 1
                continue
            
            cand_id = cand.get('candidate_id')
            text = extract_text(cand)
            heuristics = calculate_heuristics(cand)
            
            candidates.append({
                'id': cand_id,
                'raw_cand': cand,
                'text': text,
                'heuristics': heuristics
            })
            if i % 10000 == 0 and i > 0:
                print(f"[{datetime.now()}] Processed {i} candidates...")

    print(f"[{datetime.now()}] Filtered {filtered_count} honeypots.")
    print(f"[{datetime.now()}] Valid candidates: {len(candidates)}")

    # Pass 2: TF-IDF Scoring
    print(f"[{datetime.now()}] Computing TF-IDF embeddings...")
    corpus = [JD_TEXT] + [c['text'] for c in candidates]
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=10000)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    jd_vector = tfidf_matrix[0]
    cand_vectors = tfidf_matrix[1:]
    
    print(f"[{datetime.now()}] Computing cosine similarity...")
    cosine_sim = cosine_similarity(jd_vector, cand_vectors).flatten()

    # Pass 3: Final Scoring and Ranking
    print(f"[{datetime.now()}] Applying heuristics and ranking...")
    for i, cand in enumerate(candidates):
        sem_score = cosine_sim[i]
        final_score = sem_score * cand['heuristics']
        cand['sem_score'] = sem_score
        cand['final_score'] = final_score

    # Sort candidates by final_score descending
    # To handle ties deterministically, sort by final_score desc, then id asc
    candidates.sort(key=lambda x: (-x['final_score'], x['id']))
    
    top_100 = candidates[:100]

    # Pass 4: Output to CSV
    print(f"[{datetime.now()}] Generating reasoning and writing to {args.out}...")
    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['candidate_id', 'rank', 'score', 'reasoning'])
        for rank, cand in enumerate(top_100, 1):
            reasoning = generate_reasoning(cand['raw_cand'], cand['sem_score'], cand['heuristics'])
            # Ensure score is monotonically non-increasing. It is because we sorted by -final_score.
            writer.writerow([cand['id'], rank, f"{cand['final_score']:.6f}", reasoning])

    print(f"[{datetime.now()}] Done!")

if __name__ == '__main__':
    main()
