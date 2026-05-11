from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    position = Column(String)
    department = Column(String)
    role = Column(String, default='user')
    status = Column(String, default='Pending')
    activation_code = Column(String)
    password_hash = Column(String)

class Developer(Base):
    __tablename__ = 'developers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    folder_id = Column(String)
    posts_folder = Column(String)
    pres_folder = Column(String)
    temp_folder = Column(String)

class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True)
    title = Column(String)
    developer_id = Column(Integer)
    invite_link = Column(String)

class PendingMessage(Base):
    __tablename__ = 'pending_messages'
    id = Column(Integer, primary_key=True)
    row_id = Column(String, unique=True)
    original_chat_id = Column(String)
    original_message_id = Column(String)
    media_group_id = Column(String)
    text = Column(Text)
    file_ids = Column(JSON)
    status = Column(String, default='New')
    admin_message_id = Column(String)
    folder_url = Column(String)
    timestamp = Column(DateTime)

class LegalStatus(Base):
    __tablename__ = 'legal_status'
    id = Column(Integer, primary_key=True)
    developer_id = Column(Integer)
    status = Column(String, default='нет данных')
    history = Column(JSON, default=[])
    responsible_rd = Column(String)
    plan = Column(Text)
    last_updated = Column(DateTime)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
