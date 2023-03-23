from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from main.models import User

#===form for ===

#====now register form for the admin====
class RegisterForm(ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder':'Email', 'style':'width:400px;'}))
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder':'Username','style':'width:400px;'}))
    password=forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder':'Password', 'style':'width:400px;'}))


    class Meta:
        model = User
        fields = ['username','email','password']

    #def save(self, commit=True):
    #    user = super(RegisterForm, self).save(commit=False)
    #    user.email = self.cleaned_data['email']
    #    if commit:
    #        user.save()
    #    return user

#==now the login form

class AdminLoginForm(ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder':'Email, e.g tukore@gmail.com','style':'width:400px;'}))
    password=forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder':'Password', 'style':'width:400px;'}))
    class Meta:
        model = User
        fields = ['username','password']


class LoginForm(ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder':'Email, e.g tukore@gmail.com','style':'width:400px;'}))
    password=forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder':'Password', 'style':'width:400px;'}))
    class Meta:
        model = User
        fields = ['username','password']

#===form for payments=====
class PaymentForm(forms.Form):
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder':'Phone Number e.g 256706626855','style':'width:300px;'}
        ),
        max_length=12
    )


#====form to update the password===
class UpdatePasswordForm(forms.Form):
    OldPassword = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder':'Enter old Password'}
        )
    )
    NewPassword= forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder':'Enter New Password'}
        )
    )
    ConfirmPassword= forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder':'Confirm New Password'}
        )
    )


#===form to update the admin password===
class UpdateAdminPasswordForm(forms.Form):
    OldPassword = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder':'Enter old Password'}
        )
    )
    NewPassword = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder':'Enter New Password'}
        )
    )
    ConfirmPassword = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder':'Confirm New Password'}
        )
    )


class WithdrawForm(forms.Form):
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder':'Phone Number e.g 256706626855','style':'width:300px;'}
        )
    )
    amount = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder':'Amount e.g 50000','style':'width:300px'})
    )

class PlatForm(forms.Form):
    amount = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder':'Amount e.g 100000 and Above','style':'width:300px'})
    )



