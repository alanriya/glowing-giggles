from fastapi import FastAPI
from .routers import query
from pydantic import BaseSettings

app = FastAPI()

origin = ["*"]

app.include_router(query.router)

# check if api is serving.
@app.get("/")
def root():
    return {"message" : "api is serving now." }