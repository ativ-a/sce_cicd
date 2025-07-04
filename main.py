from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import yaml
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    payload_nested = json.loads(payload.get("payload", "{}"))

    repo_info = payload_nested.get("repository", {})
    repo_name = repo_info.get("html_url")
    ref = payload_nested.get("ref")
    
    
    if not ref or not repo_name: 
        return {"status": "ignored" }
    
    branch = ref.split("/")[-1]

    logging.debug(f"Parsed repo {repo_name}, branch {branch}")
    
    for repo in config["repos"]: 
        if repo["name"] == repo_name and repo["branch"] == branch: 
            logging.info(f"detected push to {branch} of {repo_name}")
            break 
    
    return {"status": "ok"}