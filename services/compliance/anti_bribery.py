# anti_bribery.py
"""
Module for anti-bribery and corruption screening logic.
Add your anti-bribery compliance checks and utilities here.
"""

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
from pymongo import MongoClient

def check_anti_bribery(entity_name, data_frame):
    """
    Example function to check if an entity is flagged for anti-bribery or corruption.
    Returns True if flagged, False otherwise.
    """
    entity_row = data_frame[data_frame['Entity'] == entity_name]
    if not entity_row.empty:
        flags = entity_row.iloc[0]['Flags']
        if 'bribery' in flags.lower() or 'corruption' in flags.lower():
            return True
    return False

data = {
    "Framework": [
        "FCPA (USA)", "UK Bribery Act", "OECD Anti-Bribery Convention",
        "UNGC Principles", "OFAC/EU/UN Sanctions Lists", "ISO 37001"
    ],
    "Jurisdiction/Scope": [
        "Applies to U.S. entities and foreign entities acting in the U.S.",
        "Applies globally to entities with UK ties",
        "44 member countries (e.g., US, UK, Germany, Japan)",
        "Voluntary global initiative for businesses",
        "Global (varies by authority)",
        "International standard (voluntary certification)"
    ],
    "Key Features": [
        "- Criminalizes bribes to foreign officials\n- Requires accurate accounting controls for public companies",
        "- Criminalizes public and private bribery\n- Strict liability for 'failure to prevent bribery'",
        "- Requires criminalization of foreign bribery\n- Bans facilitation payments",
        "- Voluntary principles promoting anti-corruption practices",
        "- Cross-checking against sanctioned'[] entities lists",
        "- Provides specifications for setting up an anti-bribery management system"
    ]
}

df = pd.DataFrame(data)
print(df)  # shows the table in your terminal

# Optional: plot a bar chart of how many key features each framework has
plt.bar(df["Framework"], df["Key Features"].str.count("\n") + 1)
plt.ylabel("Number of Key Features");' '
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

def load_entities(csv_path):
    """Load entities from a CSV file. Expects columns: Entity, Flags"""
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return pd.DataFrame(columns=["Entity", "Flags"])
    return pd.read_csv(csv_path)

def get_mongo_client(uri="mongodb://localhost:27017/"):
    """Create and return a MongoDB client."""
    return MongoClient(uri)

def import_unstructured_data(collection_name, data_list, db_name="compliance"):
    """Import a list of unstructured data (dicts) into MongoDB."""
    client = get_mongo_client()
    db = client[db_name]
    collection = db[collection_name]
    if data_list:
        result = collection.insert_many(data_list)
        print(f"Inserted {len(result.inserted_ids)} documents into '{collection_name}' collection.")
    else:
        print("No data to import.")
    client.close()

# Example usage (uncomment to use):
# sample_data = [
#     {"Entity": "Example Corp", "Flags": "corruption, bribery", "Notes": "Unstructured info here."},
#     {"Entity": "Another Inc", "Flags": "none", "Notes": "No issues found."}
# ]
# import_unstructured_data("entities", sample_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anti-bribery entity screening tool")
    parser.add_argument("--entity", type=str, help="Check a specific entity by name")
    parser.add_argument("--csv", type=str, default="data/entities.csv", help="Path to entities CSV file")
    parser.add_argument("--init-db", action="store_true", help="Initialize MongoDB with entities from CSV")
    args = parser.parse_args()

    entities_df = load_entities(args.csv)
    if args.init_db:
        # Import all entities from CSV into MongoDB
        if not entities_df.empty:
            data_list = entities_df.to_dict(orient="records")
            import_unstructured_data("entities", data_list)
        else:
            print("No entities loaded to import into MongoDB.")
    elif entities_df.empty:
        print("No entities loaded.")
    elif args.entity:
        flagged = check_anti_bribery(args.entity, entities_df)
        if flagged:
            print(f"Entity '{args.entity}' is FLAGGED for anti-bribery/corruption.")
        else:
            print(f"Entity '{args.entity}' is NOT flagged.")
    else:
        flagged_entities = []
        for entity in entities_df["Entity"]:
            if check_anti_bribery(entity, entities_df):
                flagged_entities.append(entity)
        print("\nFlagged Entities:")
        if flagged_entities:
            for e in flagged_entities:
                print(f"- {e}")
        else:
            print("None flagged for anti-bribery/corruption.")
