from django.contrib import admin
from .models import UserAccount, UserAddress,BankProfile

# Register your models here.
admin.site.register(
    [
        UserAccount,
        UserAddress,
        BankProfile,
    ]
)
