from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI()

class GiftCard(BaseModel):
    id: str
    brand: str
    amount: float
    currency: str = "USD"

class OrderRequest(BaseModel):
    user_id: str
    giftcard_id: str
    payment_method: str  # "card" or "sinpe"

class OrderResponse(BaseModel):
    order_id: str
    status: str
    code: Optional[str] = None

giftcards_db = [
    GiftCard(id="1", brand="Amazon", amount=10.0),
    GiftCard(id="2", brand="Netflix", amount=15.0),
    GiftCard(id="3", brand="Spotify", amount=25.0)
]

orders_db = {}

@app.get("/giftcards", response_model=List[GiftCard])
def list_giftcards():
    return giftcards_db

@app.post("/order", response_model=OrderResponse)
def create_order(order: OrderRequest):
    giftcard = next((g for g in giftcards_db if g.id == order.giftcard_id), None)
    if not giftcard:
        raise HTTPException(status_code=404, detail="Gift card not found")
    if order.payment_method not in ["card", "sinpe"]:
        raise HTTPException(status_code=400, detail="Método de pago inválido")

    order_id = str(uuid.uuid4())
    code = f"{giftcard.brand[:3].upper()}-{uuid.uuid4().hex[:8]}"
    orders_db[order_id] = {
        "user_id": order.user_id,
        "giftcard": giftcard,
        "status": "completed",
        "code": code
    }
    return OrderResponse(order_id=order_id, status="completed", code=code)

@app.get("/order/{order_id}", response_model=OrderResponse)
def get_order(order_id: str):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    order = orders_db[order_id]
    return OrderResponse(order_id=order_id, status=order["status"], code=order["code"])
