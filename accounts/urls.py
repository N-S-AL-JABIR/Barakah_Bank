from django.urls import path
from .views import UserRegistration, UserLogin, UserLogoutView, UserAccountUpdateView

urlpatterns = [
    path("register/", UserRegistration.as_view(), name="register"),
    path("login/", UserLogin.as_view(), name="login"),
    path("logout/", UserLogoutView, name="logout"),
    path("profile/", UserAccountUpdateView.as_view(), name="profile"),
]
