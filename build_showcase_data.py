import csv
import json
import os

def build_showcase():
    csv_path = 'submission.csv'
    jsonl_path = '../candidates.jsonl'
    out_path = 'frontend/showcase_data.json'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Please run rank.py first.")
        return
        
    print("Reading top candidates from CSV...")
    top_candidates = []
    top_ids = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            top_ids.add(row['candidate_id'])
            top_candidates.append(row)
            
    # Sort them by rank just in case
    top_candidates.sort(key=lambda x: int(x['rank']))
    
    print("Extracting full profiles from JSONL...")
    profiles_dict = {}
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            cand = json.loads(line)
            cid = cand.get('candidate_id')
            if cid in top_ids:
                profiles_dict[cid] = cand
                if len(profiles_dict) == len(top_ids):
                    break # Found all
                    
    print("Combining data...")
    final_data = []
    for cand in top_candidates:
        cid = cand['candidate_id']
        profile_data = profiles_dict.get(cid, {})
        
        # Extract meaningful bits for UI
        prof = profile_data.get('profile', {})
        skills = [s.get('name') for s in profile_data.get('skills', [])]
        
        final_data.append({
            'rank': cand['rank'],
            'candidate_id': cid,
            'score': cand['score'],
            'reasoning': cand['reasoning'],
            'name': prof.get('anonymized_name', 'Unknown Candidate'),
            'headline': prof.get('headline', ''),
            'location': prof.get('location', ''),
            'years_of_experience': prof.get('years_of_experience', 0),
            'current_company': prof.get('current_company', ''),
            'skills': skills[:8] # top 8 skills
        })
        
    os.makedirs('frontend', exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2)
        
    print(f"Showcase data written to {out_path}!")

if __name__ == '__main__':
    build_showcase()
