from yookassa import Configuration, Payment
from app.core.settings import settings

Configuration.account_id = settings.yookassa_shop_id
Configuration.secret_key = settings.yookassa_secret_key


def create_payment(amount_rub_kopecks: int, description: str, return_url: str, order_id: str):
    response = Payment.create({
        "amount": {"value": f"{amount_rub_kopecks/100:.2f}", "currency": "RUB"},
        "capture": True,
        "confirmation": {"type": "redirect", "return_url": return_url},
        "description": description,
        "metadata": {"order_id": str(order_id)},
    })
    return response
