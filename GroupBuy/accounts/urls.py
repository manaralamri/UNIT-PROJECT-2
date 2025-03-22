from django.urls import path
from . import views


app_name = "accounts"


urlpatterns = [
    path('signup/', views.user_sign_up, name="sign_up"),
    path('signup/seller/', views.seller_sign_up, name='seller_sign_up'),
    path('signin/', views.sign_in, name="sign_in"),
    path('logout/', views.log_out, name="log_out"),
    path('profile/user/<user_name>/', views.profile_view, name='profile_view'),
]
