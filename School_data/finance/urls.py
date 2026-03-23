from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('fee-structures/', views.fee_structure_view, name='fee_structure'),
    path('fee-structures/add/', views.add_fee_structure_view, name='add_fee_structure'),
    path('student-fees/', views.student_fees_view, name='student_fees'),
    path('assign-fees/', views.assign_fees_view, name='assign_fees'),
    path('record-payment/', views.record_payment_view, name='record_payment'),
    path('receipt/<int:pk>/', views.payment_receipt_view, name='payment_receipt'),
    path('expenses/', views.expenses_view, name='expenses'),
    path('expenses/add/', views.add_expense_view, name='add_expense'),
    path('scholarships/', views.scholarships_view, name='scholarships'),
    path('scholarships/add/', views.add_scholarship_view, name='add_scholarship'),
    path('report/', views.financial_report_view, name='report'),
    path('generate-report/', views.generate_financial_report, name='generate_report'),
]
