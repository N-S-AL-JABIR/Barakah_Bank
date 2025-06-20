from django.db import models
from accounts.models import UserAccount
from .constants import TRANSACTION_TYPE


class Transaction(models.Model):
    account = models.ForeignKey(
        UserAccount, related_name="transactions", on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after_transaction = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null=True)
    loan_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]
