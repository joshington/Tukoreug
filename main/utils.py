import uuid,random,re, socket

def generate_ref_code():
    code = random.randint(10000, 99999)
    return code

#==create exceptiosn class
class WalletException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


from django.core.mail import EmailMessage

class Util:
    @staticmethod
    def send_email(data):
        email=EmailMessage(
            subject=data['email_subject'],body=data['email_body'],to=[data['to_email']]
        )
        email.send()
