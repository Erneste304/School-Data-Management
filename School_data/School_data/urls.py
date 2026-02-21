"""
URL configuration for School_data project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from Users.views import DashboardHomeView, CustomLoginView, LogoutView


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Base Auth Paths
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'), 
    # Central Dashboard Router
    path('dashboard/', DashboardHomeView.as_view(), name='dashboard_home'), 
    
    # App-Specific Routes (Included based on the main app structure)
    # path('api/', include('api.urls')), 
    
    # Specific Role Routes
    path('dashboard/admin/', include('Users.urls')), 
    path('dashboard/academics/', include('Academics.urls')), 
    path('dashboard/finance/', include('Finance.urls')), 
    
    # Root Landing Page / Public Notices
    path('', include('Communication.urls')), 
]