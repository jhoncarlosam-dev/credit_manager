from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('installment/<int:pk>/pay/', views.PaymentCreateView.as_view(), name='payment_create'),
]