from django.urls import path
from .api_views import APILoginView, APILogoutView, RegisterView, current_user, user_list, parent_children, user_detail, toggle_user_active

app_name = 'accounts_api'

urlpatterns = [
    path('login/', APILoginView.as_view(), name='api_login'),
    path('logout/', APILogoutView.as_view(), name='api_logout'),
    path('register/', RegisterView.as_view(), name='api_register'),
    path('me/', current_user, name='current_user'),
    path('users/', user_list, name='user_list'),
    path('users/<int:user_id>/', user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-active/', toggle_user_active, name='toggle_user_active'),
    path('children/', parent_children, name='parent_children'),
]
