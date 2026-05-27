from django.urls import path
from .api_views import APILoginView, APILogoutView, RegisterView, current_user, user_list

app_name = 'accounts_api'

urlpatterns = [
    path('login/', APILoginView.as_view(), name='api_login'),
    path('logout/', APILogoutView.as_view(), name='api_logout'),
    path('register/', RegisterView.as_view(), name='api_register'),
    path('me/', current_user, name='current_user'),
    path('users/', user_list, name='user_list'),
]
