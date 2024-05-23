from fastapi import FastAPI,HTTPException,Request,File, UploadFile
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from .db import DB
from src.utils import generate_unique_string,ist_datetime_current
import os
from fastapi.middleware.cors import CORSMiddleware

from src.s3 import upload_to_s3
from src import task_queue
from redis import Redis
from rq import Queue

from src.background_job import tag_file
@asynccontextmanager
async def lifespan(_app: FastAPI):
    await DB.connect()
    # await initialize_tables(DB)
    yield
    await DB.disconnect()

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

@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

@app.get("/heartbeat")
async def heartbeat(request: Request):
    unique_id=request.headers.get("UniqueId")
    release_version=request.headers.get("ReleaseVer")
    current_time=ist_datetime_current()
    client_ip = request.client.host if request.client else None
    values={"ip":client_ip,"creation":current_time,"unique_id":unique_id,"release_version":release_version}
    try:
        async with DB.transaction():
                id=await DB.execute("INSERT INTO Heartbeat (ip,creation,unique_id,release_version) VALUES (:ip,:creation,:unique_id,:release_version)", values=values)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    return "ok"

@app.post("/heartbeat")
async def post_heartbeat(request:Request,file: UploadFile = File(...)):
    # Check if the file was uploaded
    if not file:
        return JSONResponse(status_code=400, content={"message": "No file provided"})
    unique_id=request.headers.get("UniqueId")
    release_version=request.headers.get("ReleaseVer")
    # Here, you can process the uploaded file
    content = await file.read()
    _, extension = os.path.splitext(str(file.filename))
    filename="heartbeat/"+generate_unique_string(12) + extension
    upload_to_s3(content=content,filename=filename)
    file_link="https://beaglebucket.s3.amazonaws.com/" + filename
    client_ip = request.client.host if request.client else None
    current_time=ist_datetime_current()

    values={
         "ip":client_ip,
         "creation":current_time,
         "unique_id":unique_id,
         "release_version":release_version,
         "file_path":filename,
         "file_extension":extension[1:],
         "file_link":file_link
         }
    try:
        async with DB.transaction():
            id=await DB.execute("INSERT INTO HeartbeatUpload (ip,creation,unique_id,release_version,file_path,file_extension,file_link) VALUES (:ip,:creation,:unique_id,:release_version,:file_path,:file_extension,:file_link)", values=values)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    return {"id":id,"ip":client_ip}

@app.post("/process")
async def process(softupload_id:int,file: UploadFile = File(...)):
    file_content = await file.read()
    job_id=task_queue.enqueue(tag_file,softupload_id,file_content)
    return 