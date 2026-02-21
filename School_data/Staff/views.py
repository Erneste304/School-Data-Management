from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from Users.mixins import RoleRequiredMixin
from .models import StaffRecord
from django.utils import timezone
from Operations.utils import log_action

class StaffApprovalListView(RoleRequiredMixin, ListView):
    """
    View for Headteacher to review and approve pending staff members.
    """
    allowed_roles = ['HEAD', 'ADMIN']
    model = StaffRecord
    template_name = 'staff/staff_approvals.html'
    context_object_name = 'pending_staff'

    def get_queryset(self):
        return StaffRecord.objects.filter(is_approved=False).order_by('-hire_date')

    def post(self, request, *args, **kwargs):
        staff_id = request.POST.get('staff_id')
        action = request.POST.get('action') # 'APPROVE' or 'REJECT'
        
        staff = get_object_or_404(StaffRecord, id=staff_id)
        
        if action == 'APPROVE':
            staff.is_approved = True
            staff.save()
            
            log_action(
                user=request.user,
                action='STAFF_APPROVAL',
                module='Staff',
                description=f"Approved staff member {staff.user.get_full_name()} (ID: {staff.id})",
                request=request
            )
        elif action == 'REJECT':
            # For rejection, we might want to deactivate or just leave unapproved
            # For now, let's just log it
            log_action(
                user=request.user,
                action='STAFF_REJECTION',
                module='Staff',
                description=f"Rejected approval for staff member {staff.user.get_full_name()} (ID: {staff.id})",
                request=request
            )

        return redirect('staff:staff_approvals')
