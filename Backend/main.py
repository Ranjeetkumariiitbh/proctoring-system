# main.py
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import datetime
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MONGO = os.environ.get('MONGO','mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO)
db = client['proctoring']

class LogItem(BaseModel):
    candidateId: str
    type: str
    ts: str
    details: dict = {}

@app.post("/api/log")
async def log_event(item: LogItem):
    item_dict = item.dict()
    item_dict['received_at'] = datetime.datetime.utcnow().isoformat()
    await db.logs.insert_one(item_dict)
    return {"ok": True}

@app.post("/api/upload-video")
async def upload_video(file: UploadFile = File(...)):
    path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(path, "wb") as f:
        f.write(await file.read())
    # store reference
    await db.videos.insert_one({"filename":file.filename, "path": path, "uploaded_at": datetime.datetime.utcnow()})
    return {"ok": True}
from fastapi import FastAPI, UploadFile, File
import shutil
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/upload-video")
async def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "filename": file.filename}
from fastapi import Request

logs = []

@app.post("/api/log")
async def log_event(request: Request):
    data = await request.json()
    logs.append(data)
    return {"status": "logged", "data": data}

@app.get("/api/report")
async def get_report():
    return {"events": logs}

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# Dummy report data (baad me database ya memory se aayega)
@app.get("/api/report")
async def get_report():
    report = {
        "events": [
            {"event": "User looking away", "timestamp": "2025-09-15T12:45:00Z"},
            {"event": "Phone detected", "timestamp": "2025-09-15T12:46:20Z"}
        ]
    }
    return JSONResponse(content=report)
