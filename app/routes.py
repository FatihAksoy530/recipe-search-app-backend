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

@router.get("/search")
async def search_posts(q: str):
    body = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "headline": q
                        }
                    },
                    {
                        "prefix": {
                            "headline": q
                        }
                    }
                ]
            }
        },
        "size": 10,
        "_source": ["headline"],
    }

    response = client.search(index="news", body=body)
    return_data = []
    for hit in response['hits']['hits']:
        return_data.append(hit['_source'])
    # return as json
    return return_data

@router.get("/post/{id}")
async def get_post(id: str):
    response = client.get(index="posts", id=id)
    return response['_source']

@router.delete("/post/{id}")
async def delete_post(id: str):
    response = client.delete(index="posts", id=id)
    return response['result']

@router.put("/post/{id}")
async def update_post(id: str, post: Post):
    response = client.update(index="posts", id=id, body={"doc": post.dict()})
    return response['_id']

@router.get("/posts")
async def get_posts():
    response = client.search(index="posts", body={"query": {"match_all": {}}})
    return [hit['_source'] for hit in response['hits']['hits']]
