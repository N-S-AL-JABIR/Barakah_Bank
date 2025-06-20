from django.db import models
from django.contrib.auth.models import User
from .constants import ACCOUNT_TYPE, GENDER_CHOICES


class BankProfile(models.Model):
    total_accounts = models.IntegerField(default=0)
    active_loan_requests = models.IntegerField(default=0)
    total_balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    total_loans = models.IntegerField(default=0)
    is_bankrupt = models.BooleanField(default=False)

    def __str__(self):
        return "Bank Profile"


class UserAccount(models.Model):
    user = models.OneToOneField(User, related_name="account", on_delete=models.CASCADE)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE)
    account_no = models.IntegerField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    initial_deposit_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)

    def __str__(self):
        return str(self.account_no)


class UserAddress(models.Model):
    user = models.OneToOneField(User, related_name="address", on_delete=models.CASCADE)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip_code = models.IntegerField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return str(self.user.email)
