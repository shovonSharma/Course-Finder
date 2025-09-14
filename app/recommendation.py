import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from sklearn.preprocessing import MinMaxScaler
import os

def preprocess_data(file_path):
    # Load dataset
    df = pd.read_csv(file_path)
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")

    # Parse students
    def parse_students(x):
        x = str(x).lower().replace(",", "").strip()
        if "k" in x:
            return int(float(x.replace("k", "")) * 1_000)
        elif "m" in x:
            return int(float(x.replace("m", "")) * 1_000_000)
        return int(float(x))

    df["course_students_enrolled"] = df["course_students_enrolled"].apply(parse_students)

    # Normalize text fields
    text_cols = ["course_title", "course_organization", "course_Certificate_type", "course_difficulty"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    # Create text_for_embedding
    df["text_for_embedding"] = (
        "Title: " + df["course_title"] + ". " +
        "Organization: " + df["course_organization"] + ". " +
        "Certificate: " + df["course_Certificate_type"] + ". " +
        "Difficulty: " + df["course_difficulty"] + ". " +
        "Rating: " + df["course_rating"].astype(str) + "."
    )

    # Normalize ratings and popularity
    scaler_rating = MinMaxScaler()
    scaler_popularity = MinMaxScaler()
    df["rating_norm"] = scaler_rating.fit_transform(df["course_rating"].values.reshape(-1, 1))
    df["popularity_norm"] = scaler_popularity.fit_transform(df["course_students_enrolled"].values.reshape(-1, 1))

    # Select required columns
    df = df[[
        "course_title",
        "course_organization",
        "course_Certificate_type",
        "course_rating",
        "course_difficulty",
        "course_students_enrolled",
        "text_for_embedding",
        "rating_norm",
        "popularity_norm"
    ]]

    # Save preprocessed CSV
    preprocessed_path = file_path.replace(".csv", "_preprocessed.csv")
    df.to_csv(preprocessed_path, index=False)
    return df

def load_data(file_path):
    preprocessed_path = file_path.replace(".csv", "_preprocessed.csv")
    required_columns = [
        "course_title",
        "course_organization",
        "course_Certificate_type",
        "course_rating",
        "course_difficulty",
        "course_students_enrolled",
        "text_for_embedding",
        "rating_norm",
        "popularity_norm"
    ]
    if os.path.exists(preprocessed_path):
        df = pd.read_csv(preprocessed_path)
        if all(col in df.columns for col in required_columns):
            return df
    print("Preprocessing CSV...")
    return preprocess_data(file_path)

# Load data
df = load_data("data/coursea_data.csv")

# Initialize model and ChromaDB client
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="data/chroma_db")

# Check if collection exists, create if not
try:
    collection = client.get_collection(name="courses")
    print(f"Loaded existing collection with {collection.count()} items")
except:
    print("Creating new ChromaDB collection...")
    collection = client.create_collection(name="courses")
    embeddings = model.encode(df["text_for_embedding"].tolist(), show_progress_bar=True)
    for idx, row in df.iterrows():
        collection.add(
            ids=[str(idx)],
            embeddings=[embeddings[idx]],
            metadatas=[{
                "title": row["course_title"],
                "organization": row["course_organization"],
                "certificate": row["course_Certificate_type"],
                "rating": float(row["course_rating"]),
                "difficulty": row["course_difficulty"],
                "students": row["course_students_enrolled"]
            }]
        )
    print(f"Created collection with {collection.count()} items")

def detect_difficulty(query):
    q = query.lower()
    if "beginner" in q:
        return "beginner"
    elif "intermediate" in q:
        return "intermediate"
    elif "advanced" in q:
        return "advanced"
    return None

def get_candidates(query, top_k=20):
    query_embedding = model.encode([query])
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["metadatas", "distances"]
    )
    return results

def get_recommendations(query, top_k=5, alpha=0.6, beta=0.2, gamma=0.2, delta=0.1):
    user_difficulty = detect_difficulty(query)
    results = get_candidates(query, top_k=30)

    scored = []
    for i, meta in enumerate(results["metadatas"][0]):
        idx = int(results["ids"][0][i])
        similarity = 1 - results["distances"][0][i]
        rating = df.loc[idx, "rating_norm"]
        popularity = df.loc[idx, "popularity_norm"]
        difficulty_bonus = delta if (user_difficulty and meta["difficulty"].lower() == user_difficulty) else 0
        final_score = alpha * similarity + beta * rating + gamma * popularity + difficulty_bonus

        scored.append({
            "title": meta["title"],
            "organization": meta["organization"],
            "rating": meta["rating"],
            "students": meta["students"],
            "difficulty": meta["difficulty"],
            "final_score": final_score
        })

    scored = sorted(scored, key=lambda x: x["final_score"], reverse=True)
    return scored[:top_k]