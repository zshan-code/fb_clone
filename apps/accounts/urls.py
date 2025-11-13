#creating the api for the user reg, login, logout 

from django.urls import path
from .views import RegisterView, LoginView, LogoutView, MyProfileView, DeleteAccountView

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/me/", MyProfileView.as_view(), name="my-profile"),
    path("delete/", DeleteAccountView.as_view(), name="delete-account"),
]
