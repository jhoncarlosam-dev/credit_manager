# users/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from credits.models import Credit, AmortizationSchedule
from clients.models import Client
from datetime import date

@login_required
def dashboard(request):
    # Totales generales
    total_active_credits = Credit.objects.filter(status=Credit.Status.ACTIVE).count()
    total_loaned = Credit.objects.filter(status__in=[Credit.Status.ACTIVE, Credit.Status.PAID_OFF]).aggregate(Sum('amount'))['amount__sum'] or 0
    total_clients = Client.objects.count()
    
    # Cuotas vencidas (hoy mayor a due_date y estado pending)
    today = date.today()
    overdue_installments = AmortizationSchedule.objects.filter(
        due_date__lt=today,
        status=AmortizationSchedule.Status.PENDING
    ).select_related('credit__client')
    
    overdue_count = overdue_installments.count()
    overdue_total = sum(i.installment_value for i in overdue_installments)
    
    context = {
        'total_active_credits': total_active_credits,
        'total_loaned': total_loaned,
        'total_clients': total_clients,
        'overdue_count': overdue_count,
        'overdue_total': overdue_total,
        'overdue_installments': overdue_installments[:10],  # solo 10 para no saturar
    }
    return render(request, 'dashboard.html', context)