from django.urls import path
from .views import StaffApprovalListView

app_name = 'staff'

urlpatterns = [
    path('approvals/', StaffApprovalListView.as_view(), name='staff_approvals'),
]
