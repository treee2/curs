import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.db import models
from app.core.settings import settings
from aiogram import Bot

Base.metadata.create_all(bind=engine)

app = FastAPI()

bot = Bot(token=settings.telegram_bot_token)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/webhook/yookassa")
async def yookassa_webhook(request: Request):
    payload = await request.json()
    event = payload.get("event")
    obj = payload.get("object", {})
    payment_id = obj.get("id")

    if not payment_id:
        raise HTTPException(400, "No payment id")

    db: Session = SessionLocal()
    try:
        payment: models.Payment | None = db.query(models.Payment).filter_by(yookassa_payment_id=payment_id).one_or_none()
        if not payment:
            metadata = obj.get("metadata") or {}
            order_id = metadata.get("order_id")
            if order_id:
                order = db.get(models.Order, int(order_id))
                if order:
                    payment = models.Payment(order_id=order.id, yookassa_payment_id=payment_id, amount_rub=order.product.price_rub)
                    db.add(payment)
                    db.flush()
        if not payment:
            raise HTTPException(404, "Payment not found")

        order = db.get(models.Order, payment.order_id)
        if not order:
            raise HTTPException(404, "Order not found")

        if event == "payment.succeeded":
            payment.status = models.PaymentStatus.succeeded
            order.status = models.OrderStatus.paid
            db.commit()
            product = db.get(models.Product, order.product_id)
            user = db.get(models.User, order.user_id)
            file_path = product.file_path
            if not os.path.isfile(file_path):
                raise HTTPException(500, "File not found on server")
            msg = await bot.send_document(chat_id=int(user.telegram_id), document=open(file_path, "rb"), caption=f"Спасибо за покупку! {product.title}")
            delivery = models.Delivery(order_id=order.id, telegram_message_id=msg.message_id)
            order.status = models.OrderStatus.delivered
            db.add(delivery)
            db.commit()
        elif event == "payment.canceled":
            payment.status = models.PaymentStatus.cancelled
            order.status = models.OrderStatus.cancelled
            db.commit()
        return JSONResponse({"ok": True})
    finally:
        db.close()
