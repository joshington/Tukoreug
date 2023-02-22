import uuid,random,re, socket
from uuid import uuid4

import requests, json

import environ
#Initialize environment variables
from .models import*

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env('SECRET_KEY')
PUBLIC_KEY = env('PUBLIC_KEY')

enc_key = env('encryption_key')

DEFAULT_ADDRESS = 'support@tukoreug.com'


from .rave import*
# function to handle the silicon topup functionality
def silicon_top(phone_number,amount):
    url = "https://silicon-pay.com/process_payments"
    payload = json.dumps({
        "req":"mobile_money",
        "currency":"UGX",
        "phone":format_phone_number(phone_number),
        "encryption_key":enc_key,
        "amount":int(amount),
        "emailAddress":DEFAULT_ADDRESS,
        "call_back":"http://tukore.pythonanywhere.com/topup/status",
        "txRef":str(uuid4())
    })
    headers = {
        'Content-Type':'application/json'
    }
    response = requests.request("POST",url, headers=headers,data=payload)
    return response.text
