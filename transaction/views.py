from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction
from .forms import DepositForm, WithdrawForm, LoanForm, BalanceTransferForm
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum
from django.urls import reverse_lazy
from datetime import datetime
from .constants import DEPOSIT, WITHDRAWAL, LOAN, LOAN_PAID
from django.views import View
from accounts.models import BankProfile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from accounts.models import UserAccount


def send_transaction_email(user, amount, template_name, title, message_line, icon="💰"):
    formatted_time = timezone.localtime().strftime("%B %d, %Y at %I:%M %p")

    context = {
        "user": user,
        "amount": amount,
        "balance": user.account.balance,
        "time": formatted_time,
        "title": title,
        "message_line": message_line,
        "icon": icon,
    }

    email_subject = f"{icon} {title} | Barakah Bank"
    to_email = user.email

    html_message = render_to_string(template_name, context)

    email = EmailMultiAlternatives(subject=email_subject, body="", to=[to_email])
    email.attach_alternative(html_message, "text/html")
    email.send()


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = "transaction/transaction_form.html"
    model = Transaction
    title = ""
    success_url = reverse_lazy("transaction_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"account": self.request.user.account})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs
        )  # template e context data pass kora
        context.update({"title": self.title})

        return context


class DepositView(TransactionCreateMixin):
    form_class = DepositForm
    title = "Deposit Money"

    def get_initial(self):
        initial = {"transaction_type": DEPOSIT}
        return initial

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return HttpResponse("You must be logged in to perform this action.")
        amount = form.cleaned_data.get("amount")
        account = self.request.user.account
        # if not account.initial_deposit_date:
        #     now = timezone.now()
        #     account.initial_deposit_date = now
        account.balance += amount
        account.save(update_fields=["balance"])
        bank = BankProfile.objects.first()
        if bank:
            bank.total_balance += amount
            bank.save(update_fields=["total_balance"])

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully',
        )
        send_transaction_email(
            self.request.user,
            amount,
            "transaction/transaction_email.html",
            "Deposit Successful",
            "Your deposit request has been successfully completed.",
            "💰",
        )

        return super().form_valid(form)


class WithdrawView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = "withdraw Money"

    def get_initial(self):
        initial = {"transaction_type": WITHDRAWAL}
        return initial

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return HttpResponse("You must be logged in to perform this action.")
        bank = BankProfile.objects.first()
        if bank and bank.is_bankrupt:
            return HttpResponse(
                "The bank is currently bankrupt and cannot process withdrawals."
            )
        amount = form.cleaned_data.get("amount")
        account = self.request.user.account
        if amount > bank.total_balance:
            return HttpResponse("currently bank does not have enough funds to process this withdrawal.Please reduce the amount or try again later.")
        account.balance -= amount
        account.save(update_fields=["balance"])
        messages.success(self.request, f"Withdraw of {amount} was successful.")
        if bank:
            bank.total_balance -= amount
            bank.save(update_fields=["total_balance"])
            if bank.total_balance < 1000:
                bank.is_bankrupt = True
                bank.save(update_fields=["is_bankrupt"])
        send_transaction_email(
            self.request.user,
            amount,
            "transaction/transaction_email.html",
            "Withdraw Successful",
            "Your withdrawal has been completed.",
            "💸",
        )

        return super().form_valid(form)


class LoanRequestView(TransactionCreateMixin):
    form_class = LoanForm
    title = "Request For Loan"

    def get_initial(self):
        initial = {"transaction_type": LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        current_loan_count = Transaction.objects.filter(
            account=self.request.user.account, transaction_type=3
        ).count()
        if current_loan_count >= 3:
            return HttpResponse("You can only have 3 active loans at a time.")
        else:
            messages.success(
                self.request, f"Loan of {amount} was successfully sent for approval."
            )
        bank = BankProfile.objects.first()
        if bank:
            bank.active_loan_requests += 1
            bank.save(update_fields=["active_loan_requests"])
        send_transaction_email(
            self.request.user,
            amount,
            "transaction/transaction_email.html",
            "Loan Request Received",
            "Your loan request has been submitted for approval.",
            "📝",
        )

        return super().form_valid(form)


class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = "transaction/transaction_report.html"
    model = Transaction
    balance = 0
    context_object_name = "report_list"

    def get_queryset(self):
        queryset = super().get_queryset().filter(account=self.request.user.account)
        start_date_str = self.request.GET.get("start_date")
        end_date_str = self.request.GET.get("end_date")

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            queryset = queryset.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            )
            self.balance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            ).aggregate(Sum("amount"))["amount__sum"]
        else:
            self.balance = self.request.user.account.balance

        return queryset.distinct() 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"account": self.request.user.account})

        return context


class LoanPaymentView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        if loan.loan_approved:
            user_account = loan.account
            if loan.amount <= user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = 4
                loan.save()
                bank = BankProfile.objects.first()
                if bank:
                    bank.total_loans -= loan.amount
                    bank.save(update_fields=["total_loans"])
                    bank.active_loan_requests -= 1
                    bank.save(update_fields=["active_loan_requests"])
                return redirect("transaction_list")
            else:
                messages.error(request, "Insufficient balance to pay the loan.")
                return redirect("transaction_list")


class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "transaction/loan_request.html"
    context_object_name = "loans"

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account, transaction_type=3)
        return queryset


class BalanceTransferView(LoginRequiredMixin, View):
    form_class = BalanceTransferForm
    template_name = "transaction/balance_transfer.html"
    success_url = reverse_lazy("transaction_list")

    def get(self, request):
        form = BalanceTransferForm(account=request.user.account)
        return render(
            request, self.template_name, {"form": form, "title": "Balance Transfer"}
        )

    def post(self, request):
        form = BalanceTransferForm(request.POST, account=request.user.account)
        if form.is_valid():
            sender = request.user.account
            recipient_number = form.cleaned_data["recipient_account"]
            amount = form.cleaned_data["transfer_amount"]

            if sender.balance < amount:
                messages.error(request, "Insufficient balance.")
                return render(request, self.template_name, {"form": form})

            recipient = get_object_or_404(UserAccount, account_no=recipient_number)

            sender.balance -= amount
            recipient.balance += amount
            sender.save()
            recipient.save()

            Transaction.objects.create(
                account=sender,
                transaction_type=WITHDRAWAL,
                amount=amount,
                balance_after_transaction=sender.balance,
            )
            Transaction.objects.create(
                account=recipient,
                transaction_type=DEPOSIT,
                amount=amount,
                balance_after_transaction=recipient.balance,
            )

            messages.success(
                request, f"Successfully transferred ${amount} to {recipient_number}"
            )
            send_transaction_email(
                self.request.user,
                amount,
                "transaction/transaction_email.html",
                "Transfer Successful",
                "Transaction has been successfully completed.",
                "💰",
            )
            send_transaction_email(
                recipient.user,
                amount,
                "transaction/transaction_email.html",
                "Deposit Successful",
                f"You have received ${amount} from {self.request.user.first_name} {self.request.user.last_name}.",
                "💰",
            )
            return redirect("transaction_list")

        return render(
            request, self.template_name, {"form": form, "title": "Balance Transfer"}
        )
