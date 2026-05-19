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
        preferred_file = knowledge_path / f"{DOMAIN_FILE_MAP[domain]}.txt"

        if preferred_file.exists():
            return preferred_file.read_text(encoding="utf-8")

    query_embedding = model.encode([user_query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get("documents", [[]])

    if documents and documents[0]:
        return documents[0][0]

    return None