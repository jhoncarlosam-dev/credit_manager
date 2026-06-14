from django.views.generic import ListView, DetailView, CreateView, UpdateView, RedirectView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Credit, AmortizationSchedule
from clients.models import Client

class AnalystRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='analyst').exists() or self.request.user.is_superuser

# Lista de créditos (accesible por cualquier usuario logueado)
class CreditListView(LoginRequiredMixin, ListView):
    model = Credit
    template_name = 'credits/credit_list.html'
    context_object_name = 'credits'
    paginate_by = 10

    def get_queryset(self):
        queryset = Credit.objects.select_related('client').all()
        # Filtros opcionales
        client_id = self.request.GET.get('client')
        status = self.request.GET.get('status')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Client.objects.all()
        context['status_choices'] = Credit.Status.choices
        return context

# Detalle del crédito
class CreditDetailView(LoginRequiredMixin, DetailView):
    model = Credit
    template_name = 'credits/credit_detail.html'
    context_object_name = 'credit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['installments'] = self.object.installments.all().order_by('installment_number')
        return context

# Crear solicitud de crédito (solo analistas)
class CreditCreateView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = Credit
    fields = ['client', 'amount', 'term_months', 'annual_interest_rate', 'start_date']
    template_name = 'credits/credit_form.html'
    success_url = reverse_lazy('credits:credit_list')

    def form_valid(self, form):
        # El crédito se crea con estado PENDING (por defecto)
        messages.success(self.request, 'Solicitud de crédito creada exitosamente.')
        return super().form_valid(form)

# Aprobar crédito (solo analistas) -> cambia estado a ACTIVE y genera cuotas
class CreditApproveView(LoginRequiredMixin, AnalystRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('credits:credit_detail', kwargs={'pk': self.kwargs['pk']})

    def get(self, request, *args, **kwargs):
        credit = get_object_or_404(Credit, pk=self.kwargs['pk'])
        if credit.status == Credit.Status.PENDING:
            credit.status = Credit.Status.ACTIVE
            credit.save()  # El método save() genera las cuotas si es ACTIVE
            messages.success(request, 'Crédito aprobado. Se generó la tabla de amortización.')
        else:
            messages.warning(request, 'Este crédito no puede ser aprobado.')
        return redirect(self.get_redirect_url())

# Rechazar crédito (solo analistas)
class CreditRejectView(LoginRequiredMixin, AnalystRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('credits:credit_detail', kwargs={'pk': self.kwargs['pk']})

    def get(self, request, *args, **kwargs):
        credit = get_object_or_404(Credit, pk=self.kwargs['pk'])
        if credit.status == Credit.Status.PENDING:
            credit.status = Credit.Status.REJECTED
            credit.save()
            messages.info(request, 'Crédito rechazado.')
        else:
            messages.warning(request, 'No se puede rechazar un crédito en este estado.')
        return redirect(self.get_redirect_url())