from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard, name='dashboard'),
    path('create/', views.create_bill, name='create_bill'),
    path('invoice/<int:bill_id>/', views.invoice_view, name='invoice'),
]