from django.shortcuts import render
from django.views.generic import FormView
from .forms import UserRegistrationForm, UserUpdateForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.shortcuts import redirect
from .models import BankProfile


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

    def get_success_url(self):
        return reverse_lazy("home")


def UserLogoutView(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("login")


class UserAccountUpdateView(View):
    template_name = "accounts/profile.html"

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
