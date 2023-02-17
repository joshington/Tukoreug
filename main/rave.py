import uuid,random,re, socket
from uuid import uuid4

from rave_python import Rave
import environ
#Initialize environment variables
from .models import*

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env('SECRET_KEY')
PUBLIC_KEY = env('PUBLIC_KEY')

DEFAULT_ADDRESS = 'bbosalj@gmail.com'

rave = Rave(PUBLIC_KEY, SECRET_KEY, usingEnv = False)


#==getting the ip address currently
def get_ip_address():
    host_name = socket.gethostname()
    IP_Addr = socket.gethostbyname(host_name)
    return IP_Addr

#====format the phonenumber, since its arequirement by flutterwave
def format_phone_number(phone_number):
    code = str(256)
    if phone_number[:3] != code:
        phonenumber = code+phone_number[1:]#since we dont need the zero at the beginning
        if len(phonenumber) == 12:
            return phonenumber
    else:
        phonenumber = phone_number
        return phone_number

#====function to make momo payment===
def make_momo_payment(amount, phonenumber,user,email=DEFAULT_ADDRESS):
    IP=get_ip_address()
    txRef = str(uuid4())
    payment = Payment(
        transaction_ref=txRef,amount=amount,user=user
    )
    payment.save()
    payload = {
        'amount':amount,
        'email':email,
        'phonenumber':format_phone_number(phonenumber),
        "redirect_url": "https://rave-webhook.herokuapp.com/receivepayment",
        'IP':IP
    }
    return payload

def transfer_money_to_phone(phone, amount, username="Unknown User"):
    details = {
        "account_bank":"MPS",
		"account_number":format_phone_number(phone),
		"amount":amount,
        "currency":"UGX",
        "beneficiary_name":username,
        "meta":{
            "sender": "Flutterwave Developers",
            "sender_country": "UGA",
            "mobile_number": "256760810134"
        }
    }
    res = rave.Transfer.initiate(details)
    return res


