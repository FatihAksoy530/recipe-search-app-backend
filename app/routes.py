# routes.py
from fastapi import APIRouter
from elasticsearch import Elasticsearch
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()

client = Elasticsearch(
    cloud_id=settings.ELASTIC_CLOUD_ID,
    http_auth=(settings.ELASTIC_USERNAME, settings.ELASTIC_PASSWORD),
)

class Post(BaseModel):
    title: str
    content: str

@router.post("/post/")
async def create_post(post: Post):
    response = client.index(index="posts", body=post.dict())
    return response['_id']

@router.get("/search/")
async def search_posts(q: str):
    body = {
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["title", "content"]
            }
        }
    }
    response = client.search(index="posts", body=body)
    return [hit['_source'] for hit in response['hits']['hits']]
