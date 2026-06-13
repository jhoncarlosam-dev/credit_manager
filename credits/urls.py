from django.urls import path
from . import views

app_name = 'credits'

urlpatterns = [
    path('', views.CreditListView.as_view(), name='credit_list'),
    path('<int:pk>/', views.CreditDetailView.as_view(), name='credit_detail'),
    path('create/', views.CreditCreateView.as_view(), name='credit_create'),
    path('<int:pk>/approve/', views.CreditApproveView.as_view(), name='credit_approve'),
    path('<int:pk>/reject/', views.CreditRejectView.as_view(), name='credit_reject'),
    # Agregaremos el pago después
]