from django.urls import path
from .api_views import APILoginView, APILogoutView

app_name = 'accounts_api'

urlpatterns = [
    path('login/', APILoginView.as_view(), name='api_login'),
    path('logout/', APILogoutView.as_view(), name='api_logout'),
]
