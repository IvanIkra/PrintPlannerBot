import uuid
from yookassa import Configuration, Payment


def generate_link(cost):
    Configuration.account_id = 372469
    Configuration.secret_key = "test_37qQzxT76VcdeyTKrY0POixW7gbrRP_AHPOCbWUFREI"

    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": str(cost),
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url"
        },
        "description": "Заказ №72"
    }, idempotence_key)

    # get confirmation url
    json_file = payment.json()
    payment_id = payment.payment_method.id
    confirmation_url = payment.confirmation.confirmation_url
    return confirmation_url, payment_id