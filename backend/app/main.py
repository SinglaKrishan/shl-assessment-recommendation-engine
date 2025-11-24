from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

# ---------- FastAPI App Setup ----------
app = FastAPI(
    title="SHL Assessment Recommendation Engine",
    description="AI-powered recommendation system using embeddings + metadata scoring",
    version="1.0",
)

# CORS: allow React dev server
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Request Body Model ----------
class Query(BaseModel):
    query: str
    k: int = 6
    remote_preferred: Optional[bool] = None
    adaptive_preferred: Optional[bool] = None
    test_type_preference: Optional[str] = None  # "K", "S", "P", ...


# ---------- Load Vector DB + Embedding Model ----------
CHROMA_PATH = Path(__file__).resolve().parent.parent / "vectorstore" / "chroma"

chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))

# IMPORTANT: same name as we used in create_embeddings.py
collection = chroma_client.get_or_create_collection(name="shl_products")

model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------- Health Check ----------aur genf
@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Recommendation Endpoint ----------
@app.post("/recommend")
def recommend(body: Query):
    # 1) Embed the query
    query_embedding = model.encode(body.query).tolist()

    # 2) Semantic search in Chroma
    res = collection.query(
        query_embeddings=[query_embedding],
        n_results=20,  # get more, then rerank
    )

    final_results = []

    for i in range(len(res["ids"][0])):
        meta = res["metadatas"][0][i]
        distance = res["distances"][0][i]

        # distance -> similarity (1 - d)
        semantic_score = 1 - distance
        score = semantic_score

        # --- Metadata boosts ---

        # Remote preference
        if body.remote_preferred is not None:
            if body.remote_preferred and meta.get("remote_support") == "Yes":
                score += 0.05
            elif not body.remote_preferred and meta.get("remote_support") == "No":
                score += 0.05

        # Adaptive preference
        if body.adaptive_preferred is not None:
            if body.adaptive_preferred and meta.get("adaptive_support") == "Yes":
                score += 0.05

        # Test type preference
        if body.test_type_preference:
            if body.test_type_preference in (meta.get("test_type") or ""):
                score += 0.1

        final_results.append({
            "rank": i + 1,
            "score": round(float(score), 4),
            "name": meta.get("name"),
            "url": meta.get("url"),
            "test_type": meta.get("test_type"),
            "remote_support": meta.get("remote_support"),
            "adaptive_support": meta.get("adaptive_support"),
            "job_levels": meta.get("job_levels"),
            "long_description": meta.get("long_description"),
        })

    # 3) Sort by score descending and take top k
    final_results = sorted(final_results, key=lambda x: x["score"], reverse=True)

    return {"results": final_results[: body.k]}
