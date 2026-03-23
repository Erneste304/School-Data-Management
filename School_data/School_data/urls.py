from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('schools/', include('schools.urls', namespace='schools')),
    path('academics/', include('academics.urls', namespace='academics')),
    path('discipline/', include('discipline.urls', namespace='discipline')),
    path('finance/', include('finance.urls', namespace='finance')),
    path('activities/', include('activities.urls', namespace='activities')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('livestream/', include('livestream.urls', namespace='livestream')),
    path('audit/', include('audit.urls', namespace='audit')),
    path('staff/', include('staff.urls', namespace='staff')),
    path('dashboard/', include('accounts.dashboard_urls', namespace='dashboard')),
    path('api/accounts/', include('accounts.api_urls', namespace='accounts_api')),
    path('api/schools/', include('schools.api_urls', namespace='schools_api')),
    path('api/academics/', include('academics.api_urls', namespace='academics_api')),
    path('', RedirectView.as_view(url='/accounts/login/'), name='home_root'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)