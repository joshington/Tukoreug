import environ
#Initialize environment variables
env = environ.Env()
environ.Env.read_env()

from django.shortcuts import render,redirect
from django.contrib.auth import login as auth_login, authenticate,logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required

import random, math, requests
from django.http import JsonResponse
from django.urls import reverse

from rave_python import Rave,  Misc, RaveExceptions

from .forms import*
# Create your views here.
from .models import*
from .rave import*
from .silicon import*
#===just use global variables

#=====initially store the email as yours and modify it through the global scope
current_email = "bbosalj@gmail.com"
min_amount = 20000

show_popup = False


#===function to define a list of user with their grandparents incase they have
child_grands = []


#==view to handle the callback data sent to us from silicon pay
@require_http_methods(['GET', 'POST'])
def handle_callback(request):
    #now pick the data sent to me by silicon pay
    #{
    #    "status":"successful",
    #    "amount":"xxxxx",
    #    "txRef":"XXXX",
    #    "nework_ref":"XXXXX",
    #    "msisdn":"XXXXX",
    #    "secure_hash":"XXXXX"
    #    }
    #===the above is the response that is sent to the callback url
    status = request.GET.get('status', None)
    amount = request.GET.get('amount', None)
    user=request.user
    wallet = Wallet.objects.get(owner=user)
    if status == "successful":
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

                            return redirect(reverse("main:dash")) #since user is still the same user
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
        messages.success(request, "Deposit was successful")
        return redirect(reverse("main:dash")) #since user is still the same user
    else:
        messages.error(request, "Transaction didnot complete")
        return redirect(reverse("main:dash")) #since user is still the same user






@require_http_methods(['GET', 'POST'])
def payment_response(request):
    status = request.GET.get('status', None)
    tx_ref = request.GET.get('tx_ref', None)


    print(status)
    print(tx_ref)

    #====now get the details u passed
    user = User.objects.get(email=current_email)
    #now get the wallet details and increment the balance
    wallet = Wallet.objects.get(owner=user)
    if status == "successful":
        #update the wallet details, i dont need to store the
        #now get the details balance,
        user.paid = True
        user.save()#saving the paid
        old_balance = wallet.balance #===after getting the old balance we have to increment it
        new_balance = old_balance+min_amount
        wallet.balance = new_balance
        wallet.save()#saving the wallet
        #====now adding the referral algorithm that the parent earns
        #first check if user is child and then reward the parent after
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

                            return redirect(reverse("main:dash")) #since user is still the same user
                        except GrandParent.DoesNotExist:
                            pass
                    else:
                        #now means child has no grandparent so share of the grandparent is taken up by company
                        admin = Stats.objects.all().first()
                        admin_balance = admin.balance
                        admin_profits = admin.profits


                        co_earnings = min_amount*0.5
                        admin.balance = admin_balance + co_earnings

                        admin.profits = admin_profits + co_earnings
                        return redirect(reverse("main:dash")) #since user is still the same user
                return redirect(reverse("main:dash")) #since user is still the same user
            else:
                return redirect(reverse("main:dash")) #since user is still the same user
        except Child.DoesNotExist:
            pass
        messages.success(request, "Deposit was successful")
        return redirect(reverse("main:dash")) #since user is still the same user
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
        return redirect(reverse("main:dash"))
    return render(request, "main/index.html", {})

#===authentication
def signup(request):
    form = RegisterForm()
    return render(request, "main/profile.html", {"form":form})

#=====add  anew signup view
def signtrue(request):
    if request.user.is_authenticated:
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
                stats_now = Stats.objects.create(
                    balance=int(0),
                    deposits = int(0),
                    widthdraws = int(0),
                    nousers = int(0),
                    no_active_users=int(0),profits = int(0)
                )
                stats_now.save()
                #since i dont need to create data for every new user but just update the first
                #===initiating the model but i have to increment the attributes later on
                return render(request, "main/dashboard.html", {
                    "wallet":user_wallet,
                    "obj":user,
                    "authed":authed, #since i need to use it in the side panel
                    "messages":messages
                })
            messages.error(request, "Unsuccessful registration. Invalid information")
        form = RegisterForm()
        authed = True
        return render(request, "main/profile.html", {"register_form": form,"authed":authed})

#====choose package
def choose_package(request):
    user = request.user
    return render(request, "main/package.html", {"obj":user})



#===code to handle the individual packages
#===also u have to give user input to add in the phone
def handle_input_phone(request):
    user = request.user
    if request.method == "POST":
        global min_amount, show_popup
        form = PaymentForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            #go ahead with the transaction
            response = silicon_top(phone,min_amount)
            if response['status'] == "Successful":
                show_popup = True#  i think i have to put this in the global scope
                messages.success(request, "Success, complete transaction")
                #return render(request, "main/showup.html", {"show":show_popup})
                #==redirect to the callback
                return redirect(reverse("main"))

            else:
                show_popup = False
                return render(request, "main/showup.html", {"show":show_popup})
    form = PaymentForm()
    return render(request,"main/topup.html", {"form":form, "obj":user, "show":show_popup})


def handle_silver(request):
    global min_amount
    user = request.user
    if user:
        user.account_type = "SILVER"
        min_amount = user.get_deposit
        #==now instead here bring in the silicon pay funcs
        return redirect(reverse("main:handle_input"))

    else:
        pass
    #==go ahead and pass in the deposit amount

#===anyway just go ahead for now with individual funcs
def handle_gold(request):
    global min_amount
    user = request.user
    if user:
        user.account_type = "GOLD"
        min_amount = user.get_deposit
        return redirect(reverse("main:deposit"))
    return

#====now for the platinum bit of it
def handle_platinum(request):
    user = request.user
    if request.method == "POST":
        global min_amount
        form = PlatForm(request.POST)
        if form.is_valid():
            amount = int(form.cleaned_data['amount'])
            if amount >= 100000:
                min_amount = amount
                user.account_type = "PLATINUM"
                return redirect(reverse("main:deposit"))
            else:
                messages.error(request, "Minimum amount is 100000")
                form = PlatForm()
                return render(request,"main/platinum.html", {"form":form, "obj":user})
        return
    form = PlatForm()
    return render(request,"main/platinum.html", {"form":form, "obj":user})




#===function to handle the platinum since user has to add in their amount

def process_payment(name,email):
    auth_token = env('SECRET_KEY')
    hed = {'Authorization':'Bearer ' + auth_token}
    phone='0706626855'
    data = {
        "tx_ref":''+str(math.floor(1000000 + random.random()*9000000)),
        "amount":min_amount,
        "currency":"UGX",
        "redirect_url":"http://tukore.pythonanywhere.com/callback",
        "payment_options":"card",
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
        }
    }
    url = ' https://api.flutterwave.com/v3/payments'
    response = requests.post(url, json=data, headers=hed)
    response = response.json()
    link = response['data']['link']
    return link

#=========
#====since the callback doesnt provide for me the user am going to supply to this function
#==create a global dictionary

def store_details(email,amount):
    details = {"email":email, "amount":amount}
    return details

def deposit(request):
    username = request.user.username;
    email = request.user.email

    #==to modify the email you have to first specify the global keyname
    global current_email; current_email = email
    return redirect(process_payment(username,email))


#======now handling the withdraws===
def withdraw(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = WithdrawForm(request.POST)
            if form.is_valid():
                phone = form.cleaned_data['phone']
                amount = form.cleaned_data['amount']
                user = request.user
                #now that u have the user get the earnings of the user so that to withdraw
                #they can withdraw after 1 month
                user_wallet = Wallet.objects.get(owner=user)
                if user_wallet:
                    earnings = user_wallet.earnings
                    balance = user_wallet.balance
                    withdraws = user_wallet.withdraws
                    if balance > int(amount):
                        #initially what to withdraw from has to be greater than the maount
                        try:
                            res = transfer_money_to_phone(phone,int(amount),user.username)
                            print(res)
                            if not res['error']:
                                #meaning that the error is False, go ahead and update the wallet
                                new_balance = balance - int(amount)
                                #earn_current = earnings - int(amount)
                                withdraw = withdraws + int(amount)

                                user_wallet.balance = new_balance
                                if user_wallet.balance < user.get_deposit:
                                    user.paid = False
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
                                return redirect(reverse("main:dash"))
                        except RaveExceptions.IncompletePaymentDetailsError as e:
                            return render(request, "main/withdraw.html", {"form":form})
        form =  WithdrawForm()
        return render(request, "main/withdraw.html", {"form":form})
    else:
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



#====now to logout the user
@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return redirect(reverse("main:login"))

#====actual login view====
def logintrue(request):
    if request.user.is_authenticated:
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
                auth_login(request, user)
                messages.success(request, "Login successful.")
                user_wallet = Wallet.objects.select_related().get(owner=user)
                return render(request, "main/dashboard.html", {
                    "obj":user, "wallet":user_wallet
                })
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    form = LoginForm()
    return render(request, "main/login.html",{"form":form})


#===now work on view to start accepting payments=====

#======now view to retrieve the admin details====
def get_admin(request):
    nousers = User.objects.all().count();
    #activeusers = [k for k in User.objects.filter(paid==True)]
    #activeusers = len(activeusers)


    if Stats.objects.all().count() > 0:
        admin_stat = Stats.objects.all().first()
        balance = admin_stat.balance; deposits = admin_stat.deposits;
        withdraws = admin_stat.widthdraws;
        profits = admin_stat.profits
    else:
        balance = 0; deposits = 0;withdraws = 0; profits = 0

    return render(request, "main/admindash.html", {
        "balance":balance,
        "deposits":deposits,
        "withdraws":withdraws,
        "nousers":nousers,"profits":profits})

def dashboard(request):
    if request.user.is_authenticated:
        user = request.user
        user_wallet = Wallet.objects.select_related().get(owner=user)
            #now that we have the user model

        return render(request, "main/dashboard.html", {
            "obj":user, "wallet":user_wallet
        })
    else:
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