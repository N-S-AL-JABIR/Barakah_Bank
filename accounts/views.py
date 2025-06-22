from django.shortcuts import render, redirect
from django.views.generic import FormView
from .forms import UserRegistrationForm, UserUpdateForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.shortcuts import redirect
from .models import BankProfile
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from transaction.views import send_transaction_email


class UserRegistration(FormView):
    template_name = "accounts/user_registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        print(form.cleaned_data)
        user = form.save()
        login(self.request, user)
        bank = BankProfile.objects.first()
        if bank:
            bank.total_accounts += 1
            bank.save(update_fields=["total_accounts"])

        else:
            BankProfile.objects.create(total_accounts=1)
        return super().form_valid(form)


class UserLogin(LoginView):
    template_name = "accounts/user_login.html"
    title =  "Login"

    def get_success_url(self):
        return reverse_lazy("home")


def UserLogoutView(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("login")

class UserProfileView(View):
    template_name = "accounts/profile.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        return render(request, self.template_name, {"user": request.user})

class UserAccountUpdateView(View):
    template_name = "accounts/edit_profile.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
        return render(request, self.template_name, {"form": form})


class ChangePasswordView(View):
    template_name = "accounts/change_password.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        return render(request, self.template_name)

    def post(self, request):
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        user = request.user
        if not check_password(current_password, user.password):
            messages.error(request, "Current password is incorrect.")
            return render(request, self.template_name)
        if new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
            return render(request, self.template_name)
        user.set_password(new_password)
        user.save()
        send_transaction_email(
            self.request.user,
            None,
            "transaction/transaction_email.html",
            "Password Change Successful",
            "Your password has been successfully changed.",
            "🔒",
        )
        return redirect("profile")
