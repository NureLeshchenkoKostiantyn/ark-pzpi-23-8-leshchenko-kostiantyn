from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import jwt  # Це для JWT
from .database import engine, SessionLocal
from . import models, schemas

# Автоматично створюємо таблиці при запуску
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Система контролю касових черг")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === НОВИЙ ЕНДПОІНТ: Авторизація (JWT) ===
@app.post("/auth/login")
def login():
    # Простий демо-логін (фіксований користувач для лабораторної)
    token = jwt.encode({"user_id": 1, "role": "manager"}, "secret_key", algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

# === Створення каси ===
@app.post("/checkouts")
def create_checkout(data: schemas.CheckoutCreate, db: Session = Depends(get_db)):
    checkout = models.Checkout(name=data.name, is_active=True)
    db.add(checkout)
    db.commit()
    db.refresh(checkout)

    # Автоматично створюємо чергу для нової каси
    queue = models.Queue(checkout_id=checkout.id, people_count=0)
    db.add(queue)
    db.commit()

    return {"message": "Касу створено", "id": checkout.id, "name": checkout.name}

# === НОВИЙ ЕНДПОІНТ: Список усіх кас ===
@app.get("/checkouts")
def get_checkouts(db: Session = Depends(get_db)):
    checkouts = db.query(models.Checkout).all()
    return [{"id": c.id, "name": c.name, "is_active": c.is_active} for c in checkouts]

# === Список усіх черг ===
@app.get("/queues")
def get_queues(db: Session = Depends(get_db)):
    queues = db.query(models.Queue).all()
    return [{"queue_id": q.id, "checkout_id": q.checkout_id, "people_count": q.people_count, "updated_at": q.updated_at} for q in queues]

# === Оновлення черги (від IoT-клієнта) ===
@app.put("/queues/{queue_id}")
def update_queue(queue_id: int, data: schemas.QueueUpdate, db: Session = Depends(get_db)):
    queue = db.query(models.Queue).filter(models.Queue.id == queue_id).first()
    if not queue:
        return {"error": "Чергу не знайдено"}
    queue.people_count = data.people_count
    queue.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Чергу оновлено", "people_count": data.people_count}

# === НОВИЙ ЕНДПОІНТ: Надсилання сповіщення ===
@app.post("/notifications")
def send_notification(data: schemas.NotificationCreate, db: Session = Depends(get_db)):
    # Тут у реальній системі було б збереження або WebSocket
    return {"status": "sent", "message": data.message}

# Головна сторінка
@app.get("/")
async def root():
    return {"message": "Сервер працює! Перейдіть на /docs для Swagger UI"}