from django.contrib import admin

# from transactions.models import Transaction
from .models import Transaction
from accounts.models import BankProfile
from transaction.views import send_transaction_email
from django.contrib import messages


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "account",
        "amount",
        "balance_after_transaction",
        "transaction_type",
        "loan_approved",
    ]

    def save_model(self, request, obj, form, change):
        if obj.transaction_type == 3:
            bank = BankProfile.objects.first()
            if bank:
                if obj.amount > bank.total_balance:
                    messages.error(
                        request,
                        "Insufficient bank balance to approve this loan.",
                    )
                    return
                bank.total_loans += obj.amount
                bank.active_loan_requests -= 1
                bank.save(update_fields=["total_loans"])
                bank.save(update_fields=["active_loan_requests"])
                obj.account.balance += obj.amount
                obj.balance_after_transaction = obj.account.balance
                obj.account.save()
            send_transaction_email(
                obj.account.user,
                obj.amount,
                "transaction/transaction_email.html",
                "Loan Approved",
                "Your loan has been approved and credited to your account.",
                "✅",
            )
        else:
            messages.error(
                request,
                "Only loan transactions can be processed through this admin interface.",
            )

        super().save_model(request, obj, form, change)
