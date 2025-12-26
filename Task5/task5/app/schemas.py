from pydantic import BaseModel

class CheckoutCreate(BaseModel):
    name: str

class QueueUpdate(BaseModel):
    people_count: int

class NotificationCreate(BaseModel):
    message: str