from django.urls import path
from .views import UserRegistration, UserLogin, UserLogoutView, UserAccountUpdateView,ChangePasswordView,UserProfileView

urlpatterns = [
    path("register/", UserRegistration.as_view(), name="register"),
    path("login/", UserLogin.as_view(), name="login"),
    path("logout/", UserLogoutView, name="logout"),
    path("edit_profile/", UserAccountUpdateView.as_view(), name="edit_profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("profile/", UserProfileView.as_view(), name="profile"),
]
