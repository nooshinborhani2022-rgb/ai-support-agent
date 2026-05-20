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
    if domain:
        domains = domain if isinstance(domain, list) else [domain]

    combined_contexts = []
    combined_sources = []

    for single_domain in domains:
        source_id = DOMAIN_FILE_MAP.get(single_domain)

        if source_id:
            preferred_file = knowledge_path / f"{source_id}.txt"

            if preferred_file.exists():
                combined_contexts.append(
                    preferred_file.read_text(encoding="utf-8")
                )
                combined_sources.append(f"{source_id}.txt")

    if combined_contexts:
        return {
            "context": "\n\n".join(combined_contexts),
            "source": combined_sources,
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