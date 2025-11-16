from django.urls import path
from .views import AccountantDashboardView, InvoiceListView

urlpatterns = [
    
    path('', AccountantDashboardView.as_view(), name='accountant_dashboard'),
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),

]