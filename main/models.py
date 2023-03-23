from django.db import models,IntegrityError, transaction
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
#==creating ==first authentication models for user
from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.utils.translation import ugettext_lazy as _

from .utils import generate_ref_code
import random
import uuid

#===now the user manager
class UserManager(BaseUserManager):
    def _create_user(self,username, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self,username, email, password, **extra_fields):
        return self._create_user(username,email,password,False,False,**extra_fields)

    def create_superuser(self,username,email,password, **extra_fields):
        user=self._create_user(username,email, password, True, True, **extra_fields)
        return user

Accounts = (
    ('SILVER','Silver'),
    ('GOLD', 'Gold'),
    ('PLATINUM', 'Platinum'),
)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=254, blank=False, default='bosa')
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=254,blank=False)
    paid = models.BooleanField(default=False)
    ref_code = models.CharField(max_length=12) #for generating the unique code.
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    now_admin = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    ref_link = models.URLField()
    account_type = models.CharField(max_length=8, choices=Accounts,default="SILVER")

    total_deposits = models.PositiveIntegerField(default=0)
    total_withdraws = models.PositiveIntegerField(default=0)
    total_balance = models.PositiveIntegerField(default=0)
    total_profits = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()


    #====add a function to generate a referral link

    def __str__(self):
        return self.email

    class Meta:
        unique_together = ("username","email")#username and email should be unique

    def save(self, *args, **kwargs):
        if not self.ref_code:
            #go ahead and generate 4 random numbers
            code = generate_ref_code()
            self.ref_code = code
        if not self.ref_link:
            link = "https://www.tukoreug.com/referrals/"+str(self.ref_code)
            self.ref_link = link
        super().save()


    #===define a decorator here to return the deposit amount baing on the package
    @property
    def get_deposit(self):
        deposit = 0
        if self.account_type == "SILVER":
            deposit = 20000
        elif self.account_type == "GOLD":deposit = 50000
        elif self.account_type == "PLATINUM":
            deposit >= 100000 #hoping this code works, but i think it does
        return deposit




#=====now we need to create the parent models and child models======
class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    is_parent = models.BooleanField(default=False)
    is_grandparent = models.BooleanField(default=False)
    no_children = models.IntegerField(default=0)#will need to count the no of children parent has
    no_grand_children = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    @property
    def get_no_children(self):
        if self.is_parent:
            children = self.no_children
            children += 1

    @property
    def get_no_grandchildren(self):
        if self.is_grandparent:
            grandchildren = self.no_grand_children
            grandchildren += 1

    #getting the grand children
    @property
    def get_grandchildren(self):
        grand_children = []
        if self.is_grandparent:
            if self.no_grand_children > 0:
                pass

#====now its time to go ahead and construct the child model of the parent
class Child(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    parent = models.ForeignKey(Parent, on_delete=models.PROTECT)
    #JUSTIFYING THAT one parent can have many children, but one child cant have many parents.
    is_child = models.BooleanField(default=False)
    is_grandchild = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

#===now the GrandChild model as well
    #===function to check if the child has a grand parent or not
    @property
    def has_grand_parent(self):
        if self.is_grandchild:return True
        else:return False

#====man i cant rule out that i need the grand parent
class GrandParent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,default='user1')
    child_parent = models.ForeignKey(Parent, on_delete=models.PROTECT,default='parent1')
    grand_child = models.ForeignKey(Child, on_delete=models.PROTECT,default='child1')

    def __str__(self):
        return self.user.username


#===initially the payments model
class Payment(models.Model):
    Statuses = (
        ('PENDING','Pending'),
        ('COMPLETE', 'Complete'),
        ('FAILED', 'Failed'),
    )
    Categories = (
        ('TOP_UP','Top Up'),
        ('WITHDRAW', 'Withdraw')
    )
    id= models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    status = models.CharField(max_length=8, choices=Statuses,default="PENDING")
    transaction_ref = models.UUIDField(default=uuid.uuid4)
    amount = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,db_constraint=False)
    category = models.CharField(max_length=8,choices=Categories,default="TOP_UP")


    def __str__(self) -> str:
        return str(self.id)

#====now working on the
class Wallet(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    balance=models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(User,on_delete=models.CASCADE,db_constraint=False,related_name='user')
    earnings = models.PositiveIntegerField(default=0)
    bonus = models.PositiveIntegerField(default=0)
    withdraws = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return str(self.owner)

#====i need another model for handling the general statistics

class Stats(models.Model):
    balance=models.PositiveIntegerField(default=0)
    deposits = models.PositiveIntegerField(default=0)
    widthdraws = models.PositiveIntegerField(default=0)
    nousers = models.IntegerField(default=0)
    no_active_users = models.IntegerField(default=0)
    profits = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.deposits)

#==target is to create the wallet immediately after creating the user
#====creating a model for fake testimonials
class Testimonials(models.Model):
    name = models.CharField(max_length=15,default="mapeera")
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name





@transaction.atomic
@receiver(post_save, sender=User)
def create_wallet(sender,instance, created, **kwargs):
    """
         a wallet for every new user instantly
    """
    if created:
        if instance.now_admin:
            admin_stats = Stats(
                balance=0,
                deposits=0,
                widthdraws=0,
                nousers=User.objects.all().exclude(now_admin=True).count(),
                no_active_users=User.objects.filter(paid=True).count(),
                profits=0
            )
            admin_stats.save()
        try:
            #go ahead and create the wallet
            wallet=Wallet(
                balance=0, owner=instance,earnings=0,bonus=0
            )
            wallet.save()
            print("saving wallet... now")
        except IntegrityError as e:
            raise e

