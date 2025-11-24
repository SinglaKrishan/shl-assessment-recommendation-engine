# SHL Assessment Recommendation Engine

This project is an **AI-powered assessment recommendation engine** built as part of the **SHL Research Intern – Generative AI Assignment**.  
It intelligently recommends the most relevant **Individual Test Solutions** from SHL’s product catalog based on **free-text user queries**, using **semantic search (embeddings) + metadata-based reranking**.

---

## 🎯 Problem Statement
Given a free-text hiring or assessment requirement query (e.g.,  
> _“Software engineering coding assessment for freshers with Java skills”_),  
the system must:

- Recommend the most relevant **Individual Test Solutions**
- Exclude packaged job-based assessments
- Return top-K best-fit options with semantic meaning
- Support metadata preferences (Remote / Adaptive / Test Type)
- Produce a **submission.csv** file using query dataset for evaluation

---

## 🚀 Key Features
- 377 **Individual Test Solutions scraped** via Playwright
- **Detailed metadata extraction** (description, job levels, test type, remote, adaptive)
- **Vector embeddings** using `all-MiniLM-L6-v2`
- **ChromaDB vector store**
- **FastAPI backend**
- **React + Tailwind UI** (Dark/Light mode)
- **Advanced reranking** with metadata boost scoring
- **CSV output generation for SHL evaluation queries**

---

## 🧠 System Architecture
```mermaid
flowchart LR
    %% ====== OFFLINE PIPELINE ======
    subgraph OFFLINE["Offline Data & Embedding Pipeline"]
        A1[Playwright + BeautifulSoup Scraper\n(scrape_shl_catalog.py)] --> A2[catalog_raw.json\n(Individual Test Solutions)]
        A2 --> A3[Detail Scraper\n(scrape_details.py)]
        A3 --> A4[catalog_full.json\n(+ descriptions, job levels)]
        A4 --> A5[Embedding Generator\n(create_embeddings.py)]
        A5 --> A6[Chroma Vector DB\n(collection: shl_products)]
    end

    %% ====== ONLINE RECOMMENDATION FLOW ======
    subgraph ONLINE["Online Recommendation System"]
        U[User in Browser] --> FE[React + Vite + Tailwind UI\n(Dark/Light mode, filters)]
        FE -->|POST /recommend\nAxios| API[FastAPI Backend]

        API -->|Encode query\n(all-MiniLM-L6-v2)| EMB[SentenceTransformer Model]
        EMB -->|Query embedding| VDB[ChromaDB Vector DB]

        VDB -->|Top-N nearest neighbours| RANK[Reranking & Scoring Layer\nSemantic + metadata boosts]
        RANK -->|Top-K results| FE

        FE -->|View Details → SHL URL| U
    end

    %% ====== SUBMISSION GENERATION ======
    subgraph EVAL["Evaluation"]
        DS[Gen_AI Dataset.xlsx] --> SUB[generate_submission.py]
        SUB --> CSV[submission.csv]
    end

## 🧮 Recommendation Logic

### Processing Steps
| Step | Action |
|------|--------|
| 1 | Encode query using SentenceTransformer embeddings |
| 2 | Get Top-N semantic matches from ChromaDB |
| 3 | Apply metadata boost scoring |
| 4 | Sort by final score |
| 5 | Return Top-K recommendations |

### 📌 Scoring Boost Rules
| Rule | Score |
|------|-------|
| Remote preference match | +0.05 |
| Adaptive preference match | +0.05 |
| Test type match (K/S/P) | +0.10 |

---

## 🏗 Tech Stack

### Backend
- Python, FastAPI, Uvicorn
- SentenceTransformers (`all-MiniLM-L6-v2`)
- ChromaDB Vector Store
- Playwright + BeautifulSoup
- Pandas, OpenPyXL

### Frontend
- React (Vite)
- TailwindCSS
- Axios
- Dark / Light mode toggle

---

## 💻 How to Run

### 1. Start Backend
```bash
cd backend
conda activate shlrec
uvicorn app.main:app --reload

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev

### 3. Access Application
Open `http://localhost:5173` in your browser.

### 4. Generate Submission File
```bash
cd backend
python tools/generate_submission.py

### project Structure
```shl-assessment-recommendation-engine/
├── backend/
│   ├── app/main.py
│   ├── data/
│   ├── embeddings/
│   ├── vectorstore/
│   └── tools/generate_submission.py
├── frontend/
├── scraper/
├── submission.csv
├── architecture.png
└── README.md
```