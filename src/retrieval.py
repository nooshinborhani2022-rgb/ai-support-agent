from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()

collection = client.get_or_create_collection(name="nexa_knowledge")

knowledge_path = Path("knowledge_base")
DOMAIN_FILE_MAP = {
    "account": "login",
    "billing": "billing",
    "charge": "refund",
    "security": "fraud",
    "order": "orders"
}

documents = []
ids = []

for idx, file_path in enumerate(knowledge_path.glob("*.txt")):
    content = file_path.read_text(encoding="utf-8")

    documents.append(content)
    ids.append(file_path.stem)

if documents:
    existing = collection.count()

    if existing == 0:
        embeddings = model.encode(documents).tolist()

        collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids
        )


def retrieve_support_context(user_query, domain=None, top_k=1):
    if domain and domain in DOMAIN_FILE_MAP:
        source_id = DOMAIN_FILE_MAP[domain]
        preferred_file = knowledge_path / f"{source_id}.txt"

        if preferred_file.exists():
            return {
                "context": preferred_file.read_text(encoding="utf-8"),
                "source": f"{source_id}.txt",
                "score": 1.0,
            }

    query_embedding = model.encode([user_query]).tolist()[0]

    results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k,
    include=["documents", "distances"]
    )

    documents = results.get("documents", [[]])
    ids = results.get("ids", [[]])
    distances = results.get("distances", [[]])

    if documents and documents[0]:
        source = ids[0][0] + ".txt" if ids and ids[0] else "unknown"

        similarity_score = None

        if distances and distances[0]:
            similarity_score = round(1 - distances[0][0], 3)

        return {
            "context": documents[0][0],
            "source": source,
            "score": similarity_score,
        }

    return None