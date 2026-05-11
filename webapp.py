from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from models import Session, PendingMessage, User
import json

router = APIRouter()

@router.get("/app", response_class=HTMLResponse)
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@router.get("/review", response_class=HTMLResponse)
async def review():
    with open("review.html", "r", encoding="utf-8") as f:
        return f.read()

@router.get("/api/proposals")
async def api_proposals():
    session = Session()
    proposals = session.query(PendingMessage).filter_by(status='New').all()
    result = []
    for p in proposals:
        result.append({
            "rowId": p.row_id,
            "chatId": p.original_chat_id,
            "text": p.text,
            "fileIds": json.loads(p.file_ids) if p.file_ids else [],
            "timestamp": p.timestamp.isoformat() if p.timestamp else ""
        })
    session.close()
    return result
