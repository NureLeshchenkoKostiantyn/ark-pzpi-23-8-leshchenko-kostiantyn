from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from datetime import datetime
import jwt
import shutil  # для резервної копії
from .database import engine, SessionLocal
from . import models, schemas
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Система контролю касових черг - ЛР №3")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Бізнес-логіка: прогнозування та сповіщення
@app.put("/queues/{queue_id}/process")
def process_queue(queue_id: int, db: Session = Depends(get_db)):
    queue = db.query(models.Queue).filter(models.Queue.id == queue_id).first()
    if not queue:
        raise HTTPException(status_code=404, detail="Чергу не знайдено")

    average_time_per_person = 2
    estimated_time = queue.people_count * average_time_per_person

    if queue.people_count > 10:
        notification = {"message": f"Черга на касі {queue.checkout_id} перевищує 10 людей! Відкрити додаткову касу."}
    else:
        notification = {"message": "Черга в нормі"}

    return {
        "estimated_wait_time_minutes": estimated_time,
        "notification": notification
    }

# Адміністрування
class UserCreate(BaseModel):
    username: str
    role: str = "manager"

@app.post("/admin/users")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = models.User(username=user_data.username, role=user_data.role)
    db.add(user)
    db.commit()
    return {"message": "Користувача створено", "username": user_data.username, "role": user_data.role}

@app.post("/admin/backup")
def create_backup(db: Session = Depends(get_db)):
    db_path = r"C:\Users\miner\OneDrive\Desktop\queue_system_lab2\data\queue.db"
    backup_filename = f"C:\\Users\\miner\\OneDrive\\Desktop\\queue_system_lab2\\backup_queue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Файл queue.db не знайдено")

    shutil.copy(db_path, backup_filename)
    log = models.AdminLog(action=f"Створено резервну копію {backup_filename}")
    db.add(log)
    db.commit()
    return {"message": "Резервну копію створено", "file": backup_filename}

@app.get("/admin/logs")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(models.AdminLog).all()
    return [{"action": log.action, "timestamp": str(log.timestamp)} for log in logs]

# Попередні функції
@app.post("/auth/login")
def login():
    token = jwt.encode({"role": "admin"}, "secret_key", algorithm="HS256")
    return {"access_token": token}

@app.get("/queues")
def get_queues(db: Session = Depends(get_db)):
    queues = db.query(models.Queue).all()
    return [
        {
            "id": q.id,
            "checkout_id": q.checkout_id,
            "people_count": q.people_count,
            "updated_at": str(q.updated_at)
        } for q in queues
    ]

@app.post("/checkouts")
def create_checkout(data: schemas.CheckoutCreate, db: Session = Depends(get_db)):
    checkout = models.Checkout(name=data.name)
    db.add(checkout)
    db.commit()
    db.refresh(checkout)
    queue = models.Queue(checkout_id=checkout.id, people_count=0)
    db.add(queue)
    db.commit()
    return {"id": checkout.id}

@app.put("/queues/{queue_id}")
def update_queue(queue_id: int, data: schemas.QueueUpdate, db: Session = Depends(get_db)):
    queue = db.query(models.Queue).filter(models.Queue.id == queue_id).first()
    if queue:
        queue.people_count = data.people_count
        db.commit()
    return {"message": "Оновлено"}

@app.get("/")
def root():
    return {"message": "Сервер ЛР №3 працює!"}