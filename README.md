# Course-Finder
is an intelligent course recommendation system which uses semantic search and a multi-factor ranking algorithm to provide highly relevant course suggestions.
For this project I used the coursera-dataset.

## Tech Stack
<u>Backend & API</u>: FastAPI, Python

<u>Embeddings</u>: sentence-transformers (all-MiniLM-L6-v2)

<u>Vector Database</u>: ChromaDB (as a persistent client)

<u>Frontend</u>: Streamlit

<u>Data Processing</u>: Pandas, Scikit-learn

<u>Deployment</u>: Docker, Docker Compose

## ✨ Features
#### Semantic Search: 
Utilizes vector embeddings and ChromaDB to understand the meaning behind your queries, finding courses that are conceptually similar, not just textually.

#### Multi-Factor Ranking: 
Ranks courses based on a weighted combination of semantic similarity, user ratings, and student enrollment (popularity).

#### Dynamic Difficulty Filtering: 
Automatically detects and prioritizes courses with a matching difficulty level (e.g., beginner, intermediate, advanced) if specified in the user's query.

#### Robust API: 
A FastAPI backend serves recommendations, ensuring a fast and scalable service.

#### Streamlit Frontend: 
A clean and responsive Streamlit user interface allows for easy searching and visualization of results.

#### Containerized Deployment: 
Uses Docker and Docker Compose for a seamless, cross-platform setup, making it easy to run the entire application with a single command

## Project structure

```bash
.
├── app/
│   ├── main.py             # FastAPI backend API
│   ├── recommendation.py   # Core recommendation logic & data handling
├── frontend/
│   ├── app.py              # Streamlit frontend UI
├── data/
│   ├── coursera_data.csv   # Raw dataset
│   └── chroma_db/          # Persistent ChromaDB store
├── Dockerfile              # Docker build instructions
├── docker-compose.yml      # Multi-container setup for Docker
└── requirements.txt        # Python dependencies
```

## Project DEMO
A demo of the project is given here.
[Course-Finder demo](https://youtu.be/2r2vd6Y2vMM)


## Screenshot
![UI1](https://github.com/shovonSharma/Course-Finder/blob/main/UI1.jpg)
![UI2](https://github.com/shovonSharma/Course-Finder/blob/main/UI2.jpg)
![UI3](https://github.com/shovonSharma/Course-Finder/blob/main/UI3.jpg)


## 🔍 In-depth Analysis
### Semantic Search & Vector Embeddings
Instead of a basic keyword search, this system uses sentence transformers to convert both the user's query and the course descriptions into numerical vectors (embeddings).  The semantic similarity between these vectors is calculated to find courses with a similar meaning to the user's query, even if they don't share keywords. This allows for a more intuitive and accurate search experience, like finding "data analysis" courses when searching for "learning to work with spreadsheets."

### The Ranking Algorithm
The core of the recommendation engine is a scoring function that combines multiple factors to provide well-rounded recommendations. The final score for each candidate course is calculated using a weighted average:

Final Score = (α * Similarity) + (β * Rating) + (γ * Popularity) + (δ * Difficulty Bonus)

The weights (α, β, γ, δ) are adjustable parameters, allowing the system to be fine-tuned. The Difficulty Bonus is a unique feature that gives a small boost to courses that match the user's explicitly stated difficulty, improving relevance for targeted searches.

### Persistent Vector Store
ChromaDB is used in persistent mode, meaning the course embeddings are stored on disk. This is a crucial design choice that prevents the need to re-embed the entire dataset every time the application starts, significantly reducing startup time after the initial run.
