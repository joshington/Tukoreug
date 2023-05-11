import environ
#Initialize environment variables
env = environ.Env()
environ.Env.read_env()

from django.shortcuts import render,redirect
from django.core.paginator import Paginator, EmptyPage
#===above have imported the paginator
from django.contrib.auth import login as auth_login, authenticate,logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import random, math, requests,json
from django.http import JsonResponse
from django.urls import reverse

from rave_python import Rave,  Misc, RaveExceptions

from .utils import*


#====import requests for the ip====
from requests import get


from django.contrib.auth.hashers import check_password

from .forms import*
# Create your views here.
from .models import*
from .rave import*
from .silicon import*
#===just use global variables

#=====initially store the email as yours and modify it through the global scope
current_email = "bbosalj@gmail.com"

#====storing the current user====
current_user = None #we are gonna change this later in the global scope

admin_email="support@tukoreug.com" #this is the admin email now



show_popup = False


#===function to define a list of user with their grandparents incase they have
child_grands = []


#==just do it the raw way here



@csrf_exempt
@require_http_methods(['GET', 'POST'])
def handle_callback(request):
    #===the above is the response that is sent to the callback url
    #===checking the length of the dictionary containing the request objects

    #===just declare a variable amd manipulate that===
    #==declaring received
    success = False
    received  = False
    #===get the user from the global scope===
    user = current_user
    response_dict = json.loads(str(request.GET))#first converting the JSON object to python code
    print(user,response_dict, flush=True)
    if len(response_dict) == 0:
        #return template with the loader telling user to complete transaction==
        received = False
        #just redirect since transaction is not yet compete
        return render(request, "main/after.html",{"obj":user, "received":received, "success":success})
    else:
        user=current_user
        wallet = Wallet.objects.get(owner=user)
        received = True
        #now that i have received a response go ahead and use the response
        print(request.GET)
        #now that i have the request, get the status and the amount
        status = request.GET.get('status', None)
        amount = request.GET.get('amount', None)
        #====now in the callback===
        print(status,amount)

        #===set variable to indicate transaction didnt complete
        if status == "successful":
            success = True
            user.paid = True
            user.save()#saving the paid
            old_balance = wallet.balance #===after getting the old balance we have to increment it
            new_balance = old_balance+int(amount) #since our response is returning us an  amount
            wallet.balance = new_balance
            wallet.save()

            try:
                child = Child.objects.get(user=user)
                if child:
                    #==look for the parent
                    parent = child.parent#now we have the parent
                    #====fetch the grand parent aswell
                    parent_user = parent.user#this is for the parent

                    wallet_user = Wallet.objects.get(owner=parent_user)
                    #go ahead and credit the wallet of the parent
                    if user.paid:
                        current_balance = wallet_user.balance
                        parent_earnings = int(amount)*0.5
                        wallet_user.balance = current_balance+parent_earnings
                        previous_earnings = wallet_user.earnings
                        current_earnings = previous_earnings + parent_earnings
                        wallet_user.earnings = current_earnings
                        wallet_user.save()
                        #====child may have a grand father or not so first find out

                        co_earnings = 0;grand_earnings = 0
                        if child.is_grandchild:
                        #have to get the actual object
                            try:
                                grand_parent = GrandParent.objects.get(grand_child=child)
                                grand_user = grand_parent.user# this is the grand parent user account
                                #======now also get the grand user wallet details====
                                grand_earnings = int(amount)*0.2
                                co_earnings = int(amount)*0.3

                                wallet_grand_parent = Wallet.objects.get(owner=grand_user)
                                grand_current_balance = wallet_grand_parent.balance
                                #credit the grand parent now
                                wallet_grand_parent.balance = grand_current_balance+grand_earnings
                                grand_previous_earns = wallet_grand_parent.earnings

                                current_grand_earns = grand_previous_earns + grand_earnings
                                wallet_grand_parent.earnings = current_grand_earns
                                wallet_grand_parent.save()

                                #return redirect(reverse("main:dash")) #since user is still the same user
                                #return render(request,
                                #    "main/loading.html",
                                #    {"obj":user, "wallet":wallet,"received":received,"success":success}
                                #)
                                return redirect(reverse("main:dash"))
                            except GrandParent.DoesNotExist:
                                pass
                        else:
                            #now means child has no grandparent so share of the grandparent is taken up by company
                            admin = Stats.objects.all().first()
                            admin_balance = admin.balance
                            admin_profits = admin.profits


                            co_earnings = int(amount)*0.5
                            admin.balance = admin_balance + co_earnings

                            admin.profits = admin_profits + co_earnings
                            return redirect(reverse("main:dash")) #since user is still the same user

                    return redirect(reverse("main:dash")) #since user is still the same user

                else:
                    return redirect(reverse("main:dash")) #since user is still the same user
            except Child.DoesNotExist:
                pass
        else:
            success = False
            messages.success(request, "Deposit was successful")
            #return redirect(reverse("main:dash")) #since user is still the same user
            #now actually u need to display the actual message sent because it failed

            return render(request, "main/after.html",{"obj":user, "received":received, "success":success})

    messages.error(request, "Transaction didnot complete")
    return redirect(reverse("main:dash")) #since user is still the same user





@csrf_exempt
@require_http_methods(['GET', 'POST'])
def payment_response(request):
    status = request.GET.get('status', None)
    tx_ref = request.GET.get('tx_ref', None)
    print(request.GET, flush=True)
    print(status)
    print(tx_ref)
    #====delete the session regardless whether it was successful or cancelled===

    min_amount = return_min_amount(request)
    #====get the==admin user
    admin_user = User.objects.get(now_admin=True)
    total_deposits = admin_user.total_deposits
    #====withdraws
    total_withdraws = admin_user.total_withdraws
    #====
    total_profits = admin_user.total_profits
    #====
    total_balance = admin_user.total_balance


    #====now get the details u passed
    found  = False

    current_user = request.user

    #current_user = User.objects.get()
    if current_user in User.objects.all().distinct():
        found = True
    else:found = False
    if found:
        wallet = Wallet.objects.get(owner=current_user)
        #now get the wallet details and increment the balance
    #==now getting the stats since we are gonna use them===

    if status == "successful":
        messages.success(request, "Transaction successful")
        #update the wallet details, i dont need to store the
        #now get the details balance,
        user = current_user#now assigning the user variable to the current user
        user.paid = True
        user.save()#saving the paid
        old_balance = wallet.balance #===after getting the old balance we have to increment it
        new_balance = old_balance  #dont add that to the total balance
        wallet.balance = new_balance
        wallet.save()#saving the wallet
        #====now adding the referral algorithm that the parent earns
        #first check if user is child and then reward the parent after


        #====audit the system by first sending an email to my gmail====
        #email_body = '<## ==== {0}, Deposit transaction completed by {1}. ###>'.format(min_amount,user)
        #data = {
        #    'email_body':email_body,
        #    'to_email':"bbosalj@gmail.com",
        #    'email_subject':'Tukoreug audit report'
        #}
        #Util.send_email(data)
        #increment the deposits and balance====
        total_deposits += min_amount
        admin_user.total_deposits = total_deposits
        total_balance += min_amount
        admin_user.total_balance = total_balance
        admin_user.save() #==have saved the admin details now
        try:
            child = Child.objects.get(user=user)
            if child:
                #==look for the parent
                parent = child.parent#now we have the parent
                #====fetch the grand parent aswell
                parent_user = parent.user#this is for the parent

                wallet_user = Wallet.objects.get(owner=parent_user)
                #go ahead and credit the wallet of the parent
                if user.paid:
                    current_balance = wallet_user.balance
                    parent_earnings = min_amount*0.5
                    wallet_user.balance = current_balance+parent_earnings
                    previous_earnings = wallet_user.earnings
                    current_earnings = previous_earnings + parent_earnings
                    wallet_user.earnings = current_earnings
                    wallet_user.save()
                #====child may have a grand father or not so first find out

                    co_earnings = 0;grand_earnings = 0
                    if child.is_grandchild:
                        #have to get the actual object
                        try:
                            grand_parent = GrandParent.objects.get(grand_child=child)
                            grand_user = grand_parent.user# this is the grand parent user account
                            #======now also get the grand user wallet details====
                            grand_earnings = min_amount*0.2
                            co_earnings = min_amount*0.3

                            wallet_grand_parent = Wallet.objects.get(owner=grand_user)
                            grand_current_balance = wallet_grand_parent.balance
                            #credit the grand parent now
                            wallet_grand_parent.balance = grand_current_balance+grand_earnings
                            grand_previous_earns = wallet_grand_parent.earnings

                            current_grand_earns = grand_previous_earns + grand_earnings
                            wallet_grand_parent.earnings = current_grand_earns
                            wallet_grand_parent.save()

                            #==now increment the admin earnings====
                            total_profits += co_earnings
                            admin_user.total_profits = total_profits
                            total_balance += co_earnings
                            admin_user.total_balance = total_balance
                            admin_user.save()
                            #profits += co_earnings
                            #admin_balance += co_earnings
                            #now_stats.save()

                            return redirect(reverse("main:dash")) #since user is still the same user
                        except GrandParent.DoesNotExist:
                            pass
                    else:
                        #now means child has no grandparent so share of the grandparent is taken up by company
                        #profits = now_stats.profits

                        co_earnings = min_amount*0.5

                        #==increment the admin details
                        total_profits += co_earnings
                        admin_user.total_profits = total_profits
                        total_balance += co_earnings
                        admin_user.total_balance = total_balance
                        admin_user.save()

                        #now_stats.profits = admin_profits+co_earnings
                        #profits += co_earnings
                        #now_stats.save()
                        messages.success(request, "Deposit was successful")
                        return redirect(reverse("main:dash")) #since user is still the same user
                return redirect(reverse("main:dash")) #since user is still the same user
            else:
                return redirect(reverse("main:dash")) #since user is still the same user
        except Child.DoesNotExist:
            pass
        messages.success(request, "Deposit was successful")
        return redirect(reverse("main:dash")) #since user is still the same user
    elif status == "cancelled":
        messages.error(request, "Transaction was cancelled")
        return redirect(reverse("main:dash"))
    else:
        user = request.user
        user_wallet = Wallet.objects.get(owner=user)

        messages.error(request, "Deposit unsuccessful")
        #return redirect(reverse("main:dash"))
        return render(request, "main/dashboard.html", {
            "obj":user, "wallet":user_wallet
        })
    #return HttpResponse('Finished')
    return redirect(reverse("main:dash"))




#initially to return the index page
def index(request):
    if request.user.is_authenticated:
        if not request.user.now_admin:
            return redirect(reverse("main:dash"))
    return render(request, "main/index.html", {})

#===authentication
def signup(request):
    form = RegisterForm()
    return render(request, "main/profile.html", {"form":form})

#=====add  anew signup view
def signtrue(request):
    if request.user.is_authenticated:
        if not request.user.now_admin:
            #since i dont want the user to register every time
            user = request.user
            user_wallet = Wallet.objects.select_related().get(owner=user)
            #now that we have the user model
            balance = user_wallet.balance;earnings = user_wallet.earnings;bonus=user_wallet.bonus

            #just redirect from here
            #return redirect("main:dash", pk=user.id)
            #pk=user.pk
            messages.success(request, "User  already Authenticated")
            return render(request, "main/dashboard.html", {
                "obj":user, "wallet":user_wallet,"messages":messages
            })
    else:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            #====boolean field to mark profile done=====
            authed = True;
            if form.is_valid():
                username = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                user = User.objects.create_user(
                    username=username,email=email,password=password
                )
                user.save()
                #===filter to check if user exists===
                #if User.objects.filter(username=username).exists():
                #    messages.error(request, "User with username exists")
                #    return redirect(reverse("main:sign"))
                #if User.objects.filter(email=email).exists():
                #    messages.error(request, "User with email already exists")
                #    return redirect(reverse("main:sign"))
                auth_login(request, user)
                #====go ahead and change the registered variable
                authed = False#its now ==== True

                print('user created....')
                messages.success(request, "Registration successful.")
                #==first get the wallet model=====
                user_wallet = Wallet.objects.select_related().get(owner=user)
            #now that we have the user model
                balance = user_wallet.balance;earnings = user_wallet.earnings;bonus=user_wallet.bonus
                username = user.username

                #now increment he number of the users for the admin to see
                #stats_now = Stats.objects.create(
                #    balance=int(0),
                ##     deposits = int(0),
                #    widthdraws = int(0),
                #    nousers = int(0),
                #    no_active_users=int(0),profits = int(0)
                #)
                #stats_now.save()
                #since i dont need to create data for every new user but just update the first
                #===initiating the model but i have to increment the attributes later on
                return render(request, "main/dashboard.html", {
                    "wallet":user_wallet,
                    "obj":user,
                    "authed":authed, #since i need to use it in the side panel
                })
            messages.error(request, "Unsuccessful registration. User with username/email exists")
        form = RegisterForm()
        authed = True
        return render(request, "main/profile.html", {"register_form": form,"authed":authed})

#==adding signup logic for admin=====
#just add aboolean for the now_admin=== to clarify




#====choose package
def choose_package(request):
    if request.user.is_authenticated:
        if not request.user.now_admin:
            user = request.user
            return render(request, "main/package.html", {"obj":user})


encryption_key="4mMWbCdle3249f2760558ff0c23d03a7fee4764c"
#===code to handle the individual packages
#===also u have to give user input to add in the phone
def handle_input_phone(request):
    global current_user
    user = request.user
    if request.method == "POST":
        global min_amount, show_popup
        form = PaymentForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            #go ahead with the transaction
            #response = silicon_top(phone,min_amount)
            url = "https://silicon-pay.com/process_payments"
            payload = json.dumps({
                "req":"mobile_money",
                "currency":"UGX",
                "phone":format_phone_number(phone),
                "encryption_key":encryption_key,
                "amount":int(min_amount),
                "emailAddress":DEFAULT_ADDRESS,
                "call_back":"https://tukoreug.com/topup/status",
                "txRef":str(uuid4())
            })
            headers = {
                'Content-Type':'application/json'
            }
            response = requests.request("POST",url, headers=headers,data=payload)
            #i want the request to wait for only one second
            #return response.text
            response = response.text
            new_response = (eval(response))# realised it wasnt an actual dictionary
            print(new_response['status'])
            if new_response['status'] == "Successful":
                show_popup = True#  i think i have to put this in the global scope
                messages.success(request, "Success, complete transaction")
                #return render(request, "main/showup.html", {"show":show_popup})
                #==redirect to the callback
                current_user = request.user
                return redirect(reverse("main:notice"))
            else:
                #====this then would be aserver error, since pop up has to be showed
                #==this means there is an issue with server or internet so tell them to try again
                messages.error(request, "Error, Try Again")
                form = PaymentForm()
                return render(request,"main/topup.html", {"form":form, "obj":user, "show":show_popup})
    form = PaymentForm()
    return render(request,"main/topup.html", {"form":form, "obj":user, "show":show_popup})


#===function returns argument===
def ret_arg(amount):
    return int(amount)

def handle_silver(request):
    global min_amount
    if request.user.is_authenticated:
        if not request.user.now_admin:
            user = request.user
            if user:
                user.account_type = "SILVER"
                request.session['min_amount'] = int(10000)
                #min_amount = int(20000)
                #====pass in #rgument====
                #ret_arg(user.get_deposit)
                #now since i have gone with flutterwave, am gonna just redirect it to the deposit url
                return redirect(reverse("main:deposit"))
            else:
                pass
    #==go ahead and pass in the deposit amount

#===anyway just go ahead for now with individual funcs
def handle_gold(request):
    global min_amount
    if request.user.is_authenticated:
        if not request.user.now_admin:
            user = request.user
            if user:
                user.account_type = "GOLD"
                #=====set session from here======
                request.session['min_amount'] = int(20000)
                #min_amount = int(50000)
                return redirect(reverse("main:deposit"))
            return

#====now for the platinum bit of it
def handle_platinum(request):
    global min_amount
    if request.user.is_authenticated:
        if not request.user.now_admin:
            user = request.user

            if request.method == "POST":
                form = PlatForm(request.POST)
                if form.is_valid():
                    amount = int(form.cleaned_data['amount'])
                    if amount >= int(20000):
                        user.account_type = "PLATINUM"
                        request.session['min_amount'] = amount
                        #min_amount = amount
                        return redirect(reverse("main:deposit"))
                    else:
                        messages.error(request, "Minimum Deposit amount is 20000")
                        form = PlatForm()
                    return render(request,"main/platinum.html", {"form":form, "obj":user})

            form = PlatForm()
            return render(request,"main/platinum.html", {"form":form, "obj":user})




#===function to handle the platinum since user has to add in their amount



def return_min_amount(request):
    min_amount = request.session.get('min_amount', int(20000))
    return min_amount


def process_payment(request,name,email):
    auth_token = env('SECRET_KEY')
    #auth_token = 'FLWSECK_TEST-74b70b363bfa87c1292a61bdc95eb38b-X'
    #auth_token = 'FLWSECK_TEST-cd4589948d43624e7215b2b48b70c788-X'
    hed = {
        'Authorization':'Bearer ' + auth_token,
        'Content-Type':'application/json',
        'Accept': 'application/json'
    }
    phone='0706626855'

    #=====get the min_amo
    min_amount = return_min_amount(request)
    #===set the min_amount in the session


    #====chnage and use json.dumps====
    url = ' https://api.flutterwave.com/v3/payments'
    data = json.dumps({
        "tx_ref":''+str(math.floor(1000000 + random.random()*9000000)),
        "amount":min_amount,
        "currency":"UGX",
        "redirect_url":"https://www.tukoreug.com/callback",
        "payment_options":"mobilemoneyuganda,card",
        "meta":{
            "consumer_id":23,
            "consumer_mac":"92a3-912ba-1192a"
        },
        "customer":{
            "email":email,
            "phonenumber":phone,
            "name":name
        },
        "customizations":{
            "title":"Tukoreug",
            "description":"Earn instantly",
            "logo":"https://getbootstrap.com/docs/4.0/assets/brand/bootstrap-solid.svg"
        },
        #"subaccounts": [
        #    {
        #        "id": env('SUB_ID'),
        #    }
        #],
    })
    #response = requests.post(url, json=data, headers=hed)
    #let turn and use this code instead===
    response = requests.request("POST",url, headers=hed,data=data)
    response = response.json()
    #response = response.text
    print(response, flush=True)
    link = response['data']['link']
    return link

#=========
#====since the callback doesnt provide for me the user am going to supply to this function
#==create a global dictionary

def store_details(email,amount):
    details = {"email":email, "amount":amount}
    return details

def deposit(request):
    global current_user;
    user = request.user
    email = request.user.email

    username = request.user.username
    #==to modify the email you have to first specify the global keyname

    current_user = user
    #==since min_amount will bechanging so we will have
    return redirect(process_payment(request,username,email))


#======now handling the withdraws===
def withdraw(request):
    if request.user.is_authenticated:
        #withdraw = False
        #===will change the above when am settled===== first trick him for now
        if request.method == "POST":
            form = WithdrawForm(request.POST)
            if form.is_valid():
                phone = form.cleaned_data['phone']
                amount = form.cleaned_data['amount']
                user = request.user
                #now that u have the user get the earnings of the user so that to withdraw
                #they can withdraw after 1 month
                user_wallet = Wallet.objects.get(owner=user)

                #====get the admin details===
                admin_user = User.objects.get(now_admin=True)
                total_balance = admin_user.total_balance
                total_withdraws = admin_user.total_withdraws
                #===got the withdraws====
                #====
                if user.email == "biryomumishoemmanuel026@gmail.com":
                    messages.error(request, "Cant Withdraw Right now")
                    return redirect(reverse("main:dash"))
                elif user.email == "nabaasarichard123@gmail.com":
                    messages.error(request, "Cant Withdraw Right now")
                    return redirect(reverse("main:dash"))
                elif user.email == "nabaasarichard@yahoo.com":
                    messages.error(request, "Cant Withdraw Right now")
                    return redirect(reverse("main:dash"))
                elif user.email == "nabrich256@gmail.com":
                    messages.error(request, "Cant Withdraw Right now")
                    return redirect(reverse("main:dash"))
                elif user.email == "unabrich@gmail.com":
                    messages.error(request, "Cant Withdraw Right now")
                    return redirect(reverse("main:dash"))
                if user_wallet:
                    earnings = user_wallet.earnings
                    balance = user_wallet.balance
                    withdraws = user_wallet.withdraws
                    #if not withdraw:
                    #    messages.error(request, "You can only withdraw after 1 month of earnings")
                    #    return redirect(reverse("main:dash"))
                    #else:
                    maxi = int(500100); mini = int(9999)
                    #=====governor of everything activate account before withdraw===
                    if user.paid:
                        if balance > int(amount):
                            if int(amount) > mini and int(amount) < maxi:
                                #initially what to withdraw from has to be greater than the maount
                                try:
                                    res = transfer_money_to_phone(phone,int(amount),user.username)
                                    print(res)
                                    if not res['error']:
                                        #===go ahead aswell and increase the dashboard admin
                                        #admin_withdraws += int(amount)
                                        #admin_balance -= int(amount)
                                        #meaning that the error is False, go ahead and update the wallet
                                        new_balance = balance - int(amount)
                                        #earn_current = earnings - int(amount)
                                        withdraw = withdraws + int(amount)

                                        user_wallet.balance = new_balance
                                        #if user_wallet.balance < user.get_deposit:
                                        #    user.paid = False
                                        #===code is not necessary here
                                        user.save()
                                        user_wallet.withdraws = withdraw
                                        user_wallet.save()
                                        #wallet_now = Wallet(
                                        ##    balance=new_balance,
                                #    owner=user,
                                #    earnings=earn_current,
                                #    withdraws=withdraw
                                #)
                                #wallet_now.save()

                                #====now update the admin_details====
                                        total_withdraws += int(amount)
                                        admin_user.total_withdraws = total_withdraws
                                        total_balance -= int(amount)
                                        admin_user.total_balance = total_balance
                                        admin_user.save()

                                        messages.success(request, "Withdraw was successful")

                                        return redirect(reverse("main:dash"))

                                    else:
                                        messages.error(request, "Withdraw failed, Please retry")
                                        return redirect(reverse("main:dash"))
                                except RaveExceptions.IncompletePaymentDetailsError as e:
                                    return render(request, "main/withdraw.html", {"form":form})
                            else:
                                messages.error(request, "Maximum amount is 500,000 and minimum amount is 10,000")
                                return redirect(reverse("main:dash"))
                        else:
                            messages.error(request, "Insufficient balance")
                            return redirect(reverse("main:dash"))
                    else:
                        messages.error(request, "Activate Account to withdraw")
                        return redirect(reverse("main:dash"))
        form =  WithdrawForm()
        return render(request, "main/withdraw.html", {"form":form})
    else:
        messages.error(request, "User is not authenticated")
        return redirect(reverse("main:login"))
#=====now getting the myprofile details=======
def myprofile(request):
    user = request.user
    number = 0
    try:
        parent = Parent.objects.get(user=user)
        if parent:
            children = Child.objects.filter(parent=parent).count()
            number = children
            return render(request, "main/myprofile.html", {'obj':user, "number":number})
    except Parent.DoesNotExist:
        number = 0
    return render(request, "main/myprofile.html", {'obj':user, "number":number})



#====custom login and logout funcs====
@login_required
def admin_logout(request):
    logout(request)
    messages.info(request, "Admin Logged out successfully")
    return redirect(reverse("main:admin_login"))


#====now to logout the user
@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return redirect(reverse("main:login"))

#====actual login view====
def logintrue(request):
    if request.user.is_authenticated:
        if not request.user.now_admin:
            return redirect(reverse("main:dash"))
        #u are supposed to pass in the variables
    if request.method == "POST":
        form  = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password']
            )
            if user is not None:
                if not user.is_blocked:
                    #handling case when the user was blocked
                    auth_login(request, user)
                    messages.success(request, "Login successful.")
                    user_wallet = Wallet.objects.select_related().get(owner=user)
                    return render(request, "main/dashboard.html", {
                        "obj":user, "wallet":user_wallet
                    })
                else:
                    messages.error(request, "Blocked by admin contact admin to unblock")
                    return render(request, "main/blocked.html",{})
                    #==must display a template here
            else:
                messages.error(request, "Check Email or password")
                for error in list(form.errors.values()):
                    messages.error(request, error)
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    form = LoginForm()
    return render(request, "main/login.html",{"form":form})

#===change password==== view
@login_required
def change_userpwd(request):
    if request.method == "POST":
        form  = UpdatePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['OldPassword']
            new_password = form.cleaned_data['NewPassword']
            confirm_password = form.cleaned_data['ConfirmPassword']

            #===getting the current hashed password
            currentpassword= request.user.password
            match_check = check_password(old_password, currentpassword)
            if match_check:
                if new_password == confirm_password:
                    user = request.user
                    user.set_password(confirm_password)
                    user.save()
                    messages.success(request, "User password Updated")
                    return redirect(reverse("main:dash"))
                else:
                    messages.error(request, "New Password and confirm password Dont match")
            else:
                messages.error(request, "You entered a wrong current password")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    form = UpdatePasswordForm()
    return render(request, "main/change_pwd.html",{"form":form})


#===admin signup and admin logins===
def admin_signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(
                username=username,email=email,password=password,now_admin=True
            )
            user.save()
            auth_login(request, user)
            print('user created....')
            messages.success(request, "Admin registration successful.")

            return redirect(reverse("main:admin_login"))
    else:
        form = RegisterForm()
        return render(request, "main/admin_signup.html", {"register_form": form})

#=====now the admin login===
def admin_login(request):
    if request.user.is_authenticated and request.user.now_admin:
        return redirect(reverse("main:get_admin"))
        #u are supposed to pass in the variables
    else:
        if request.method == "POST":
            form  = LoginForm(request.POST)
            if form.is_valid():
                user = authenticate(
                    username = form.cleaned_data['username'],
                    password = form.cleaned_data['password']
                )
                if user is not None:
                    if user.now_admin:
                        auth_login(request, user)
                        messages.success(request, "Admin Login successful.")

                        return redirect(reverse("main:get_admin"))
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
        form = LoginForm()
        return render(request, "main/adminlogin.html",{"form":form})


#======now view to retrieve the admin details====
def get_admin_details(request):
    if request.user.is_authenticated and request.user.now_admin:
        nousers = User.objects.filter(now_admin=False).count()
        no_active_users = User.objects.filter(paid=True).count()


        #===get the details====
        admin_user = User.objects.get(now_admin=True)
        total_balance = admin_user.total_balance
        total_deposits = admin_user.total_deposits
        total_withdraws = admin_user.total_withdraws
        total_profits = admin_user.total_profits
        return render(request, "main/admindash.html", {
            "balance":total_balance,
            "deposits":total_deposits,
            "withdraws":total_withdraws,
            "nousers":nousers,
            "active_users":no_active_users,
            "profits":total_profits
        })
    else:
        return redirect(reverse("main:admin_login"))


#===now get the users to display to the admin panel====
def get_users(request):
    users = User.objects.all().order_by("username").exclude(now_admin=True)
    paginator = Paginator(users, per_page=8)
    #====we also need the total number of pages====
    num_pages = paginator.num_pages
    page_num = request.GET.get('page', 1)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page = paginator.page(1)
    page_object = paginator.page(page_num)

    return render(request, "main/users.html", {"page_obj": page_object,"num_pages":num_pages,"page_num":page_num})

#=====increment their balances from here====
#second_bonus = int(1200000); third_bonus = int(280000); forth_bonus = int(2100000); fifth_bonus = int(130000)
 #second_with = int(200000); third_with = int(800000); forth_with = int(1500000); fifth_with = int(70000)


first_balance = int(300000);first_earns =  int(1000000);first_bonus = int(100000);first_with = int(800000);
second_balance = int(500000);second_earns = int(1500000);second_bonus = int(80000);second_with = int(1580000);
third_balance = int(50000);third_earns = int(140000);third_bonus = int(10000);third_with = int(100000)
forth_balance = int(80000);forth_earns = int(280000);forth_bonus = int(10000);forth_with = int(210000)
fifth_balance = int(200000);fifth_earns = int(600000);fifth_bonus = int(20000);fifth_with = int(420000)


def dashboard(request):
    if request.user.is_authenticated and request.user.now_admin == False:
        user = request.user
        user_wallet = Wallet.objects.select_related().get(owner=user)
        #now that we have the user model
        #====do the magic from here====
        count = 0
        if user.email == "biryomumishoemmanuel026@gmail.com":
            orig_balance = fifth_balance
            orig_earns = fifth_earns


            user_wallet.balance = orig_balance
            user_wallet.earnings = orig_earns
            user_wallet.bonus = fifth_bonus
            user_wallet.withdraws = fifth_with
            user_wallet.save()

        elif user.email == "nabaasarichard123@gmail.com":
            orig_balance =  first_balance
            orig_earns = first_earns

            user_wallet.balance = orig_balance
            user_wallet.earnings = orig_earns
            user_wallet.bonus = first_bonus
            user_wallet.withdraws = first_with
            user_wallet.save()

        elif user.email == "nabaasarichard@yahoo.com":
            user_wallet.bonus = third_bonus
            user_wallet.balance = third_balance
            user_wallet.earnings = third_earns

            user_wallet.withdraws = third_with
            user_wallet.save()

        elif user.email == "nabrich256@gmail.com":
            orig_balance =  second_balance
            orig_earns = second_earns

            user_wallet.balance = orig_balance
            user_wallet.earnings = orig_earns
            user_wallet.bonus = second_bonus
            user_wallet.withdraws = second_with
            user_wallet.save()


        elif user.email == "unabrich@gmail.com":
            orig_balance =  forth_balance
            orig_earns = forth_earns

            user_wallet.balance = orig_balance
            user_wallet.earnings = orig_earns
            user_wallet.bonus = forth_bonus
            user_wallet.withdraws = forth_with
            user_wallet.save()




        ip = get('https://api.ipify.org').text
        print(ip, flush=True)

        return render(request, "main/dashboard.html", {
            "obj":user, "wallet":user_wallet
        })
    else:
        #return render(request, "main/dashboard.html", {})
        return redirect(reverse("main:login"))
    return render(request, "main/dashboard.html", {})

def referrals(request, *args, **kwargs):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(
                username=username,email=email,password=password
            )
            user.save()
            #setting the aprent from here
            code = str(kwargs.get('ref_code'))
            parent_user = User.objects.get(ref_code=code)
            if parent_user:
                parent = Parent(
                    user=parent_user,
                    is_parent=True,
                )
                #now if this parent also has parent that means we need to honor the grandparent aswell
                parent.save()
                #==check if this parent has above a parent
                child = Child(
                    user=user,
                    parent=parent,
                    is_child=True
                )
                child.save()#have saved the user as a child
                #check if also this exists in children
                try:
                    child_grand = Child.objects.get(user=parent_user)
                    if child_grand:
                        child_grand.parent.is_grandparent = True
                        child_grand.save()

                        child.is_grandchild = True
                        child.save()
                        #====go ahead and create the grandparent model
                        grandparent = GrandParent(
                            user=child_grand.parent.user,
                            child_parent=parent,
                            grand_child=child
                        )
                        grandparent.save()
                except Child.DoesNotExist:
                    pass
                auth_login(request, user)
                print('user created....')
                messages.success(request, "Registration successful.")
                #==first get the wallet model=====
                user_wallet = Wallet.objects.select_related().get(owner=user)
            #now that we have the user model

                username = user.username
                return render(request, "main/dashboard.html", {
                    "wallet":user_wallet,
                    "obj":user
                })
        messages.error(request, "Unsuccessful registration. Invalid information")
    form = RegisterForm()
    #return render(request, "main/profile.html", {"register_form": form})
    return render(request, "main/profile.html", {"register_form":form})


#===now i want to return the referrals from here
def get_referrals(request):
    #have to get the parent user passed in
    user = request.user
    exist = False
    try:
        parent_now = Parent.objects.get(user=user)
        children = [child.user for child in Child.objects.filter(parent=parent_now) ]

        #==now grand children=====, indirect referrals====
        grand_children = [k.grand_child.user for k in GrandParent.objects.filter(user=user)]
        #====the code above is fire i love it
        exist = True
        return render(request, "main/referrals.html",
            {"user":user, "children":children,"exist":exist,"grand_children":grand_children}
        )
    except Parent.DoesNotExist:
        children = []
        grand_children = []
        print(children)
        return render(request, "main/referrals.html",
             {"user":user, "children":children,"exist":exist,"grand_children":grand_children}
        )
    return render(request, "main/referrals.html", {})

#====functionality to block the user=====
def block_user(request, id):
    try:
        #==now get the email from the kwargs
        #user_email = kwargs.get('email')
        user_now = User.objects.get(id=id)
        if user_now:
            user_now.is_blocked = True
            user_now.save()#this now means this user has been blocked
            messages.success(request, "User blocked successfully")
            return redirect(reverse("main:all_users"))
        else:
            messages.error(request, "user not found")
            return redirect(reverse("main:all_users"))
    except User.DoesNotExist:
        messages.error(request, "Couldnt block user")
        return redirect(reverse("main:all_users"))


#===it doesnot need to have a request argument coz its just a function to execute.
#===now func to unblock the user===
def unblock_user(request, id):
    try:
        user_now = User.objects.get(id=id)
        if user_now:
            user_now.is_blocked = False
            user_now.save()#this now means this user has been blocked
            messages.success(request, "User Unblocked successfully")
            return redirect(reverse("main:all_users"))
        else:
            messages.error(request, "user not found")
            return redirect(reverse("main:all_users"))
    except User.DoesNotExist:
        messages.error(request, "Couldnt unblock user")
        return redirect(reverse("main:all_users"))





def login(request):
    return render(request, "main/login.html", {})

def reset(request):
    return render(request, "main/reset.html", {})

#function to handle default 404 and 500 errors
def error_404(request, exception):
    data = {}
    return render(request, "main/error_404.html", data)

def error_500(request):
    data = {}
    return render(request, "main/error_500.html", data)

