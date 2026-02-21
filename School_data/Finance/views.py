from django.db import models
from django.db.models import Sum
from django.views.generic import TemplateView, ListView
from Users.mixins import RoleRequiredMixin
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
        context['pending_approvals_count'] = Transaction.objects.filter(status='PENDING').count()
        context['recent_transactions'] = Transaction.objects.order_by('-transaction_date')[:5]
        context['total_unpaid'] = Invoice.objects.filter(status__in=['PENDING', 'PARTIAL']).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        return context

class InvoiceListView(RoleRequiredMixin, ListView):
    """
    View to list and filter all invoices.
    """
    allowed_roles = ['ACCOUNTANT', 'HEAD', 'ADMIN'] # Allows management oversight
    model = Invoice
    template_name = 'finance/invoice_list.html'
    context_object_name = 'invoices'

class TransactionApprovalView(RoleRequiredMixin, ListView):
    """
    View for Headteacher to review and approve pending transactions.
    """
    allowed_roles = ['HEAD', 'ADMIN']
    model = Transaction
    template_name = 'finance/transaction_approvals.html'
    context_object_name = 'pending_transactions'

    def get_queryset(self):
        return Transaction.objects.filter(status='PENDING').order_by('-transaction_date')

    def post(self, request, *args, **kwargs):
        transaction_id = request.POST.get('transaction_id')
        action = request.POST.get('action') # 'APPROVE' or 'REJECT'
        
        from django.utils import timezone
        from django.shortcuts import get_object_or_404
        
        transaction = get_object_or_404(Transaction, id=transaction_id)
        
        if action == 'APPROVE':
            transaction.status = 'APPROVED'
            transaction.approved_by = request.user
            transaction.approval_date = timezone.now()
            transaction.save()
            
            from Operations.utils import log_action
            log_action(
                user=request.user,
                action='FINANCE_APPROVAL',
                module='Finance',
                description=f"Approved transaction {transaction.id} for amount {transaction.amount_paid}",
                request=request
            )
        elif action == 'REJECT':
            transaction.status = 'REJECTED'
            transaction.save()
            
            from Operations.utils import log_action
            log_action(
                user=request.user,
                action='FINANCE_REJECTION',
                module='Finance',
                description=f"Rejected transaction {transaction.id}",
                request=request
            )

        return redirect('finance:transaction_approvals')
