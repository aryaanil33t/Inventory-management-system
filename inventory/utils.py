import string

import random

from twilio.rest import Client

from decouple import config

def generate_otp():

    otp = ''.join(random.choices(string.digits,k=4))

    return otp


def send_otp(phone,otp):
    
    account_sid = config('TWILIO_ACCOUNT_STD')
    auth_token = config('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
                                    from_=config('TWILIO_SENDER'),
                                    to=config('MY_NUMBER'),
                                    body=f'OTP for login : {otp}'
                                    )
    


def delete_otp_obj(obj):

    obj.delete()

