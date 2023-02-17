import uuid,random,re, socket

def generate_ref_code():
    code = random.randint(10000, 99999)
    return code

#==create exceptiosn class
class WalletException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

