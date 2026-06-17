# Intelligent Candidate Discovery Engine

A high-performance, precision-driven semantic ranking system designed to discover the optimal candidates from a vast talent pool. Built with scalability and computational efficiency in mind, this engine evaluates candidates against rigorous business requirements—filtering out noise, "honeypots," and mismatched profiles to deliver a truly actionable shortlist.

---

## 🏗 System Architecture & Approach

This system abandons fragile keyword-matching in favor of a robust **Hybrid Semantic-Heuristic Engine**.

1. **Streaming Data Ingestion**: Processes large datasets (e.g., 100,000+ candidates) efficiently using stream processing, ensuring low memory footprint and blazing-fast execution speeds (under 2 minutes on standard CPU).
2. **Honeypot Filtering**: Implements rigid validation rules to catch impossible profiles (e.g., zero-month expert skills, contradictory career timelines).
3. **Semantic Scoring (TF-IDF)**: Extracts structured candidate text and calculates cosine similarity against the job description using heavily-weighted bigrams to capture contextual relevance.
4. **Behavioral Heuristics Engine**: Adjusts semantic scores using powerful business-logic multipliers:
   - **Stability Metrics**: Penalizes serial "title chasers" and rewards sustained tenure.
   - **Domain Specificity**: Strongly boosts candidates with targeted product experience while penalizing pure consulting backgrounds.
   - **Recency Bias**: Prioritizes candidates with high platform activity and response rates.
5. **Programmatic Reasoning Generation**: Synthesizes exact, hallucination-free reasoning strings detailing precisely *why* a candidate matched, based strictly on the evaluated features.

---

## 🚀 Setup & Installation

### Prerequisites
- **Python:** 3.10 to 3.12 is recommended.
- **Compute:** CPU-only execution is fully supported and optimized.

### 1. Install Dependencies
Ensure you have the required scientific computing libraries installed:
```bash
pip install -r requirements.txt
```

### 2. Prepare Data
Ensure the candidate data file (`candidates.jsonl` or `candidates.jsonl.gz`) is present in the parent directory or modify the path accordingly.

---

## ⚡ Execution

To execute the ranking pipeline and generate the final output, run the following command:

```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

**Output Details:**
- The engine will systematically log its progress as it streams through the candidate pool.
- The top 100 candidates will be exported to `submission.csv`, sorted by final score.
- The output strictly conforms to standardized formats, including programmatic reasoning strings.

---

## 📊 Interactive Discovery Dashboard (Frontend UI)

This repository includes a premium, glassmorphic interactive dashboard to visually explore the generated candidate matches. The dashboard supports real-time, dynamic filtering across the shortlisted candidates.

### Launching the Dashboard

**1. Generate UI Data**
Once the core ranking script has produced `submission.csv`, generate the full profile payloads required by the UI:
```bash
python build_showcase_data.py
```
*(This extracts names, headlines, skills, and locations from the core JSONL and outputs `frontend/showcase_data.json`)*

**2. Start Local Server**
Serve the frontend directory locally:
```bash
cd frontend
python -m http.server 8000
```

**3. View the Engine**
Navigate to [http://localhost:8000](http://localhost:8000) in your web browser.

### UI Features
- **Real-Time Filtering**: Dynamically filter the shortlist by Experience Level (Fresher, Mid-Level, Senior).
- **Skill Search**: Instantly drill down candidates by specific required skills (e.g., "Python", "React", "AWS").
- **Visual Justification**: Displays the programmatic reasoning strings calculated by the backend.

---

## 🔒 Constraints & Compliance

- **Compute Boundaries**: Designed specifically to respect strict memory constraints (16GB RAM) and wall-clock execution limits (< 5 minutes).
- **Zero API Reliance**: Fully contained processing. No external API calls are made during the ranking execution, ensuring zero latency and high privacy compliance.
- **Hallucination-Free**: Reasoning is strictly generated from validated data structures, eliminating the risk of generative AI hallucinations.
