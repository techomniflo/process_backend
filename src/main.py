from fastapi import FastAPI,HTTPException,Request,File, UploadFile
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from .db import engine,Base,SoftUpload,SessionLocal
from src.utils import generate_unique_string,ist_datetime_current
import os
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from rq import Queue
from typing import AsyncGenerator
import httpx
from sqlalchemy import select

from src import task_queue
from src.background_job import tag_file

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Connect to the database
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Close the database connection
    await engine.dispose()

app=FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],  # Adjust this to the specific origins you want to allow
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


def get_mapping(items):
    rv=[]
    for i in items:
        rv.append(i._mapping)
    return rv

async def get_beaglesoftupload_with_id(id:int):
    async with SessionLocal() as session:
        async with session.begin():
            query = select(SoftUpload).filter(SoftUpload.id == id)
            result = await session.execute(query)
            softupload = result.scalar_one_or_none()
            return softupload
    return None

async def download_file_content(url:str):
    try:
        async with httpx.AsyncClient() as client:
            response=await client.get(url,timeout=20.0)
            return response.content
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"error occured {str(e)} for fetching content for url: {url}")        

async def get_file_content_from_softupload_id(id:int):
    softupload=await get_beaglesoftupload_with_id(id)
    if softupload:
        file_content = await download_file_content(softupload.file_link)
        return file_content
    else:
        raise HTTPException(status_code=404, detail=f"No entry found in database for Table softupload for id {id}")

@app.post("/process")
async def process(softupload_id:int,file: UploadFile = File(None)):
    if file:
        file_content = await file.read()
    else:
        file_content = await get_file_content_from_softupload_id(softupload_id)
    job_id=task_queue.enqueue(tag_file,softupload_id,file_content)
    return