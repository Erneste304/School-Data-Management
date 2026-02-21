from django.urls import path
from .views import AccountantDashboardView, InvoiceListView, TransactionApprovalView

urlpatterns = [
    
    path('', AccountantDashboardView.as_view(), name='accountant_dashboard'),
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('approvals/', TransactionApprovalView.as_view(), name='transaction_approvals'),

]