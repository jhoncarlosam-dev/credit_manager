from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment_list'),
    path('installment/<int:pk>/pay/', views.PaymentCreateView.as_view(), name='payment_create'),
]