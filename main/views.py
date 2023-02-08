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

from .forms import*
# Create your views here.
from .models import*

#===just use global variables

#=====initially store the email as yours and modify it through the global scope
current_email = "bbosalj@gmail.com"
min_amount = 20000





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
                parent_user = parent.user
                wallet_user = Wallet.objects.get(owner=parent_user)
                #go ahead and credit the wallet of the parent
                current_balance = wallet_user.balance
                earnings = min_amount*0.3
                wallet_user.balance = current_balance+earnings
                #now after incrementing the balance, go ahead and increment the earnings aswwell
                previous_earnings = wallet_user.earnings
                current_earnings = previous_earnings + earnings
                wallet_user.earnings = current_earnings
                wallet_user.save()
                #after saving wallet of the parent, go ahead aswell and push the rest to the admin.        
        except Child.DoesNotExist:
            pass
        messages.success(request, "Deposit was successful")
        return redirect(reverse("main:dash")) #since user is still the same user
        
    else:
        messages.error(request, "Deposit unsuccessful")
        return redirect(reverse("main:dash"))
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
            registered = False
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
                registered = True#its now ==== True
                print('user created....')
                messages.success(request, "Registration successful.")
                #==first get the wallet model=====
                user_wallet = Wallet.objects.select_related().get(owner=user)
            #now that we have the user model
                balance = user_wallet.balance;earnings = user_wallet.earnings;bonus=user_wallet.bonus
                username = user.username
                return render(request, "main/dashboard.html", {
                    "wallet":user_wallet,
                    "obj":user,
                    "registered":registered, #since i need to use it in the side panel
                    "messages":messages
                })
            messages.error(request, "Unsuccessful registration. Invalid information")
        form = RegisterForm()
        registered = False
        return render(request, "main/profile.html", {"register_form": form, "registered":registered})



def process_payment(name,email):
    auth_token = env('SECRET_KEY')
    hed = {'Authorization':'Bearer ' + auth_token}
    phone='0706626855'
    data = {
        "tx_ref":''+str(math.floor(1000000 + random.random()*9000000)),
        "amount":min_amount,
        "currency":"UGX",
        "redirect_url":"http://localhost:8000/callback",
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
    
#=====now getting the myprofile details=======
def myprofile(request):
    user = request.user
    number = 0
    try:
        parent = Parent.objects.get(user=user)
        if parent:
            number = parent.no_children
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



def dashboard(request):
    if request.user.is_authenticated:
        user = request.user
        user_wallet = Wallet.objects.select_related().get(owner=user)
            #now that we have the user model
        
        return render(request, "main/dashboard.html", {
            "obj":user, "wallet":user_wallet
        })
    else:
        return render(request, "main/dashboard.html", {})
    return render(request, "main/dashboard.html", {})

def referrals(request, *args, **kwargs):
    if request.user.is_authenticated:
        #since i dont want the user to register every time
        user = request.user
        user_wallet = Wallet.objects.select_related().get(owner=user)
            #now that we have the user model
        
        return render(request, "main/dashboard.html", {
            "obj":user, "wallet":user_wallet
        })
    else:
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
                    #set the parent now
                    #==getting the number of children
                    parent = Parent(
                        user=parent_user,
                        is_parent=True,
                    )
                    parent.save()
                    #also set the current user as achild 
                    child = Child(
                        user=user,parent=parent
                    )
                    child.save()#have saved the user as a child
                    #===now increase number of children of parent
                    parent_children = parent.no_children
                    parent.no_children = parent_children+1
                    parent.save()#have saved the number of children
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
        
        exist = True
        return render(request, "main/referrals.html", 
            {"user":user, "children":children,"exist":exist}
        )
    except Parent.DoesNotExist:
        children = []
    
        print(children)
        return render(request, "main/referrals.html",
             {"user":user, "children":children,"exist":exist}
        )
   
    return render(request, "main/referrals.html", {})
def login(request):
    return render(request, "main/login.html", {})

def reset(request):
    return render(request, "main/reset.html", {})