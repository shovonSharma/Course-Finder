from fastapi import FastAPI
from pydantic import BaseModel
from app.recommendation import get_recommendations

app = FastAPI(title="Course Recommendation API")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/recommend")
async def recommend_courses(request: QueryRequest):
    recommendations = get_recommendations(request.query, request.top_k)
    return {"recommendations": recommendations}