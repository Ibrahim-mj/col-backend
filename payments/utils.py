import random
import string
import time

import requests

from django.conf import settings


def init_payment(email, amount, callback_url=None, for_reg=False, purpose=None):
    """
    Initialize a payment with the given purpose and amount.
    """

    paystack_url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    random_string = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )  # for generating unique reference
    reference = f"REG-{int(time.time())}-{random_string}"

    if for_reg: # If the payment is for registration
        data = {
            "email": email,
            "amount": str(amount * 100),  # Paystack expects amount in kobo
            "currency": "NGN",
            "reference": reference,
            "metadata": {
                "purpose": "registration",
                "custom_fields": [
                    {
                        "display_name": "Purpose",
                        "variable_name": "purpose",
                        "value": "Registration Fee",
                    }
                ],
                
            },
        }
    else:
        data = {
            "email": email,
            "amount": amount * 100,  # Paystack expects amount in kobo
            "currency": "NGN",
            "reference": reference,
            "callback_url": callback_url,
            "metadata": {
                "purpose": purpose,
                "custom_fields": [
                    {
                        "display_name": "Purpose",
                        "variable_name": "purpose",
                        "value": purpose,
                    }
                ],
            },
        }
    response = requests.post(paystack_url, headers=headers, json=data)
    response_data = response.json()

    return response_data