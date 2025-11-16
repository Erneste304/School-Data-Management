from django.shortcuts import render
import datetime
from django.views.generic import TemplateView, ListView
from users.mixins import RoleRequiredMixin
from .models import Invoice, Transaction

# --- Accountant Portal ---
class AccountantDashboardView(RoleRequiredMixin, TemplateView):
    """
    The main dashboard view for the Accountant.
    Restricted to ACCOUNTANT role only using RoleRequiredMixin.
    """
    allowed_roles = ['ACCOUNTANT']
    template_name = 'finance/accountant_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dashboard Summary Data
        context['pending_invoices_count'] = Invoice.objects.filter(status='PENDING').count()
        context['recent_transactions'] = Transaction.objects.order_by('-transaction_date')[:5]
        context['total_unpaid'] = Invoice.objects.filter(status__in=['PENDING', 'PARTIAL']).aggregate(
            total=models.Sum('total_amount')
        )['total']
        
        return context

class InvoiceListView(RoleRequiredMixin, ListView):
    """
    View to list and filter all invoices.
    """
    allowed_roles = ['ACCOUNTANT', 'HEAD', 'ADMIN'] # Allows management oversight
    model = Invoice
    template_name = 'finance/invoice_list.html'
    context_object_name = 'invoices'
