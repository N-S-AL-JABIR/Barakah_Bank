from django.urls import path
from .views import (
    DepositView,
    WithdrawView,
    LoanRequestView,
    LoanListView,
    LoanPaymentView,
    TransactionReportView,
    BalanceTransferView,
)

urlpatterns = [
    path("deposit/", DepositView.as_view(), name="deposit"),
    path("withdraw/", WithdrawView.as_view(), name="withdraw"),
    path("loan/", LoanRequestView.as_view(), name="loan"),
    path("loan/approval/", LoanListView.as_view(), name="loan_approval"),
    path("loan/payment/<int:loan_id>", LoanPaymentView.as_view(), name="loan_pay"),
    path("transactions/", TransactionReportView.as_view(), name="transaction_list"),
    path("transfer/", BalanceTransferView.as_view(), name="balance_transfer"),
]
