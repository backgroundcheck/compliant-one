import os
import sqlite3
from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings
import argparse

# Configuration
COLLECTION_NAME = "document_collection"
COHERE_API_KEY = "ONVwImVb9P2ds0G16XGocuFSuL7o8C0eij6xZRd8"
EMBEDDING_MODEL = "embed-english-v3.0"
DB_PATH = "documents.db"

os.environ["COHERE_API_KEY"] = COHERE_API_KEY
# Initialize embeddings and vector store
embeddings = CohereEmbeddings(model=EMBEDDING_MODEL)
vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

def main():
    parser = argparse.ArgumentParser(description="Query the document vector store.")
    parser.add_argument('--query', type=str, required=False, default="Find datasets that are free and machine-readable in Bangladesh", help='Query string')
    parser.add_argument('--site', type=str, required=False, help='Site filter (e.g., bd)')
    parser.add_argument('--free', type=str, required=False, help='Free filter (true/false)')
    parser.add_argument('--machinereadable', type=str, required=False, help='Machine-readable filter (true/false)')
    parser.add_argument('-k', type=int, default=10, help='Number of results to return')
    args = parser.parse_args()

    # Build filter
    filter_clauses = []
    if args.site:
        filter_clauses.append({"site": args.site})
    if args.free:
        filter_clauses.append({"free": args.free.lower() == 'true'})
    if args.machinereadable:
        filter_clauses.append({"machinereadable": args.machinereadable.lower() == 'true'})
    filter_dict = {"$and": filter_clauses} if filter_clauses else None

    # Query vector store
    results = vector_store.similarity_search_with_score(
        query=args.query,
        k=args.k,
        filter=filter_dict
    )

    if not results:
        print("No results found.")
        return

    # Query SQLite for additional metadata
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    document_ids = [doc.metadata["document_id"] for doc, _ in results]
    placeholders = ",".join(["?"] * len(document_ids))
    cursor.execute(
        f"""
        SELECT document_id, filename, officialtitle, publisher, url
        FROM documents
        WHERE document_id IN ({placeholders})
        """,
        document_ids
    )
    db_results = cursor.fetchall()
    conn.close()

    # Combine results
    for doc, score in results:
        db_row = next((row for row in db_results if row[0] == doc.metadata["document_id"]), None)
        if db_row:
            print(f"Score: {score}")
            print(f"Filename: {db_row[1]}")
            print(f"Title: {db_row[2]}")
            print(f"Publisher: {db_row[3]}")
            print(f"URL: {db_row[4]}")
            print(f"Text: {doc.page_content}")
            print("-" * 50)

if __name__ == "__main__":
    main()