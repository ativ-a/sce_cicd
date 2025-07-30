from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import yaml
import json
import time 



from prometheus_client import start_http_server, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

start_http_server(3001)

last_smee_request = Gauge("last_smee_request_timestamp", "last request from Smee")
last_push_timestamp = Gauge("last_push_timestamp", "last Git push", ["repo"])




@app.post("/webhook")
async def webhook(request: Request):
    last_smee_request.set(time.time()) 
    payload = await request.json()
    payload_nested = json.loads(payload.get("payload", "{}"))

    repo_info = payload_nested.get("repository", {})
    repo_name = repo_info.get("html_url")
    ref = payload_nested.get("ref")
    
    
    if not ref or not repo_name: 
        return {"status": "ignored" }
    last_push_timestamp.labels(repo=repo_name).set(time.time())

    
    branch = ref.split("/")[-1]

    logging.debug(f"Parsed repo {repo_name}, branch {branch}")
    
    for repo in config["repos"]: 
        if repo["name"] == repo_name and repo["branch"] == branch: 
            logging.info(f"detected push to {branch} of {repo_name}")
            break 
    
    return {"status": "ok"}
