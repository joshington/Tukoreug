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
    path('user/admin/signup', views.admin_signup, name="admin_signup"),
    path('user/admin/login', views.admin_login, name="admin_login"),
    path('user/admin/dashboard', views.get_admin_details, name="get_admin"),
    path('user/admin/dashboard/users', views.get_users, name="all_users"),
    path('user/admin/dashboard/users/block/<int:id>', views.block_user, name="block"),
    path('user/admin/dashboard/users/unblock/<int:id>', views.unblock_user, name="unblock"),
    path('dashboard/myprofile', views.myprofile, name="myprofile"),
    path('dashboard/myprofile/update', views.change_userpwd, name="update_pwd"),
    path('dashboard/referrals', views.get_referrals, name="myrefs"),
    path('referrals/<str:ref_code>', views.referrals, name="refs"),
    path('login', views.logintrue, name="login"),
    path('logout', views.custom_logout,name="logout"),
    path('user/admin/logout', views.admin_logout,name="admin_logout"),
    path('reset', views.reset, name="reset"),
    path('deposit', views.deposit, name="deposit"),
    path('dashboard/withdraw', views.withdraw, name="withdraw"),
    path('callback', payment_response, name='payment_response'),
    #path('dashboard/top/notice', views.get_notifications, name="notice"),
    #path('topup/status', views.handle_callback, name='payment_response'),
    path('dashboard/package', choose_package, name="package"),
    path('silver',handle_silver, name="silver"),
    path('gold',handle_gold, name="gold"),
    path('package/platinum', handle_platinum, name="platinum"),
    path('package/topup',  handle_input_phone, name="handle_input"),
]

