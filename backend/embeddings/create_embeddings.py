import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "catalog_full.json"
CHROMA_PATH = Path(__file__).resolve().parent.parent / "vectorstore" / "chroma"

def create_embeddings():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    model = SentenceTransformer("all-MiniLM-L6-v2")

    texts = []
    metadata = []
    ids = []

    for i, p in enumerate(products):
        combined = f"{p['name']} {p['long_description']} {p['job_levels']}"
        texts.append(combined)
        metadata.append(p)
        ids.append(str(i))

    print("Generating embeddings...")
    embeddings = model.encode(texts, convert_to_numpy=True)

    print("Creating ChromaDB...")
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = chroma_client.get_or_create_collection(name="shl_products")

    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        metadatas=metadata,
        documents=texts
    )

    print("🎉 Embedding creation complete!")
    print(f"Saved vector DB at: {CHROMA_PATH}")

if __name__ == "__main__":
    create_embeddings()
