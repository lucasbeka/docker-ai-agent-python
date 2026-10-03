import os
from fastapi import FastAPI

app = FastAPI()

MY_PROJECT = os.environ.get("MY_PROJECT") or "This is my project"
API_KEY = os.environ.get("API_KEY")

@app.get("/")
def read_index():
    return{"hello": "world", "project_name": MY_PROJECT}