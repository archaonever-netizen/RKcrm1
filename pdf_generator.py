from fpdf import FPDF
import requests, boto3, json, datetime
from models import Session, PendingMessage
from config import S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET, TELEGRAM_BOT_TOKEN

def get_telegram_file_url(file_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
    resp = requests.get(url).json()
    if resp["ok"]:
        file_path = resp["result"]["file_path"]
        return f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    return None

def generate_pdf_and_upload(row_id: str, session):
    msg = session.query(PendingMessage).filter_by(row_id=row_id).first()
    if not msg:
        return None
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Roboto", "", "Roboto-Regular.ttf", uni=True)
    pdf.set_font("Roboto", size=12)
    pdf.cell(200, 10, txt="Redcat AI - Новое предложение", ln=1, align='C')
    pdf.multi_cell(0, 10, msg.text)
    file_ids = json.loads(msg.file_ids) if msg.file_ids else []
    for fid in file_ids:
        img_url = get_telegram_file_url(fid)
        if img_url:
            img_data = requests.get(img_url).content
            pdf.image(img_data, x=10, w=190)
    pdf.output(f"/tmp/{row_id}.pdf")
    s3 = boto3.client('s3', endpoint_url=S3_ENDPOINT,
                      aws_access_key_id=S3_ACCESS_KEY,
                      aws_secret_access_key=S3_SECRET_KEY)
    s3.upload_file(f"/tmp/{row_id}.pdf", S3_BUCKET, f"pdfs/{row_id}.pdf")
    return f"{S3_ENDPOINT}/{S3_BUCKET}/pdfs/{row_id}.pdf"
