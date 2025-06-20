from django import forms
from .models import Transaction
from accounts.models import UserAccount


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount", "transaction_type"]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop("account")
        super().__init__(*args, **kwargs)
        self.fields["transaction_type"].disabled = True
        self.fields["transaction_type"].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):
    def clean_amount(self):
        min_deposit_amount = 100
        amount = self.cleaned_data.get("amount")
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f"Minimum deposit amount is {min_deposit_amount}.$"
            )
        return amount


class WithdrawForm(TransactionForm):
    def clean_amount(self):
        min_withdraw_amount = 100
        max_withdraw_amount = 25000
        amount = self.cleaned_data.get("amount")
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f"Minimum withdraw amount is {min_withdraw_amount}$"
            )
        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f"Maximum withdraw amount is {max_withdraw_amount}$"
            )
        if amount > self.account.balance:
            raise forms.ValidationError("Insufficient balance for this transaction.")
        return amount


class LoanForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount <= 100:
            raise forms.ValidationError("Loan amount must be greater than 100$.")
        if amount > 25000:
            raise forms.ValidationError("Maximum loan amount is 25000$.")
        return amount


class BalanceTransferForm(forms.ModelForm):
    recipient_account = forms.IntegerField(label="Recipient Account Number")
    transfer_amount = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=100, label="Transfer Amount"
    )

    class Meta:
        model = Transaction
        fields = ["recipient_account", "transfer_amount"]

    def __init__(self, *args, account=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.account = account

    def clean_transfer_amount(self):
        transfer_amount = self.cleaned_data.get("transfer_amount")
        if transfer_amount < 100:
            raise forms.ValidationError("Minimum transfer amount is 100$.")
        if transfer_amount > self.account.balance:
            raise forms.ValidationError("Insufficient balance for this transaction.")
        return transfer_amount

    def clean_recipient_account(self):
        recipient_account_number = self.cleaned_data.get("recipient_account")
        if not recipient_account_number:
            raise forms.ValidationError("Recipient account number is required.")

        if recipient_account_number == self.account.account_no:
            raise forms.ValidationError(
                "You cannot transfer money to your own account."
            )

        if not UserAccount.objects.filter(account_no=recipient_account_number).exists():
            raise forms.ValidationError("Recipient account does not exist.")

        return recipient_account_number
