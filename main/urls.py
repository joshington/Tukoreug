from django.urls import path
from django.conf.urls import url
from  .import views
from main.views import*


app_name = "main"

urlpatterns = [
    path('',views.index, name="index"),
    path('signup', views.signup, name="signup"),
    path('sign', views.signtrue, name="sign"),
    #url(r'^dashboard/(?P<id>\d+)/$', views.dashboard, name='dash'),
    path('dashboard', views.dashboard, name="dash"),
    path('dashboard/myprofile', views.myprofile, name="myprofile"),
    path('dashboard/referrals', views.get_referrals, name="myrefs"),
    path('referrals/<str:ref_code>', views.referrals, name="refs"),
    path('login', views.logintrue, name="login"),
    path('logout', views.custom_logout,name="logout"),
    path('reset', views.reset, name="reset"),
    path('deposit', views.deposit, name="deposit"),
    path('dashboard/withdraw', views.withdraw, name="withdraw"),
    path('callback', payment_response, name='payment_response'),
    path('dashboard/package', choose_package, name="package"),
    path('silver',handle_silver, name="silver"),
    path('gold',handle_gold, name="gold"),
    path('package/platinum', handle_platinum, name="platinum")
]

