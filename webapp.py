from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from models import Session, PendingMessage, User, Developer, Chat, LegalStatus
from config import ADMIN_TELEGRAM_ID, S3_BUCKET, SUPABASE_URL, SUPABASE_KEY
import json, boto3
from datetime import datetime

router = APIRouter()

# Mini App главная
@router.get("/app", response_class=HTMLResponse)
async def app():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@router.get("/review", response_class=HTMLResponse)
async def review():
    with open("review.html", "r", encoding="utf-8") as f:
        return f.read()

# API для Mini App
@router.get("/api/proposals")
async def api_proposals():
    session = Session()
    proposals = session.query(PendingMessage).filter_by(status='New').all()
    result = []
    for p in proposals:
        chat = session.query(Chat).filter_by(chat_id=p.original_chat_id).first()
        developer_name = chat.title if chat else "Неизвестный чат"
        result.append({
            "rowId": p.row_id,
            "chatId": p.original_chat_id,
            "text": p.text,
            "fileIds": json.loads(p.file_ids) if p.file_ids else [],
            "developerName": developer_name,
            "timestamp": p.timestamp.isoformat() if p.timestamp else ""
        })
    session.close()
    return result

@router.get("/api/proposals/{row_id}")
async def api_proposal_detail(row_id: str):
    session = Session()
    msg = session.query(PendingMessage).filter_by(row_id=row_id).first()
    if not msg:
        raise HTTPException(404, "Не найдено")
    chat = session.query(Chat).filter_by(chat_id=msg.original_chat_id).first()
    detail = {
        "text": msg.text,
        "fileIds": json.loads(msg.file_ids),
        "developerName": chat.title if chat else "Неизвестный",
        "groupInviteLink": chat.invite_link if chat else None
    }
    session.close()
    return detail

@router.post("/api/proposals/{row_id}/{action}")
async def api_proposal_action(row_id: str, action: str, selected_file_ids: str = "", secret: str = ""):
    if secret != "R3dc4t_2026_S3cur3B4ckgr0und!":
        raise HTTPException(403, "Unauthorized")
    session = Session()
    msg = session.query(PendingMessage).filter_by(row_id=row_id).first()
    if not msg:
        raise HTTPException(404, "Не найдено")
    if action == "approvePm":
        # генерация PDF
        from pdf_generator import generate_pdf_and_upload
        pdf_url = generate_pdf_and_upload(row_id, session)
        msg.status = "Approved"
        msg.folder_url = pdf_url
        session.commit()
    elif action == "skipPm":
        msg.status = "Skipped"
        session.commit()
    elif action == "rejectPm":
        msg.status = "Rejected"
        session.commit()
    session.close()
    return {"status": "ok"}

@router.post("/api/register")
async def api_register(data: dict):
    session = Session()
    if session.query(User).filter_by(username=data.get("username")).first():
        raise HTTPException(400, "Логин занят")
    code = data.get("username")[:3].upper() + str(datetime.now().timestamp())[-5:]
    user = User(
        username=data["username"],
        first_name=data.get("firstName", ""),
        last_name=data.get("lastName", ""),
        position=data.get("position", ""),
        department=data.get("department", ""),
        status="Pending",
        activation_code=code,
        role="user"
    )
    session.add(user)
    session.commit()
    session.close()
    return {"activation_code": code}

@router.post("/api/login")
async def api_login(data: dict):
    session = Session()
    user = session.query(User).filter_by(username=data["username"]).first()
    if not user:
        raise HTTPException(400, "Неверный логин или пароль")
    if user.status != "Approved":
        raise HTTPException(400, "Аккаунт не одобрен")
    session.close()
    return {
        "user": {
            "username": user.username,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "role": user.role,
            "department": user.department,
            "position": user.position
        }
    }

# Юридический трекер (базово)
@router.get("/api/legal")
async def api_legal():
    session = Session()
    legal_list = session.query(LegalStatus).all()
    result = []
    for l in legal_list:
        dev = session.query(Developer).filter_by(id=l.developer_id).first()
        result.append({
            "developerId": l.developer_id,
            "developerName": dev.name if dev else "",
            "status": l.status,
            "responsibleRD": l.responsible_rd,
            "plan": l.plan,
            "lastUpdated": l.last_updated.isoformat() if l.last_updated else "",
            "history": json.loads(l.history) if l.history else []
        })
    session.close()
    return result

# Остальные API (загрузка файлов, разработчики и пр.) могут быть добавлены аналогично.
