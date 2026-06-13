from django.views.generic import CreateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Payment
from .forms import PaymentForm
from credits.models import AmortizationSchedule, Credit

class AnalystRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='analyst').exists() or self.request.user.is_superuser

class PaymentCreateView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'

    def get_initial(self):
        initial = super().get_initial()
        installment_id = self.kwargs.get('pk')  # viene de la URL: payments/installment/<pk>/pay/
        schedule = get_object_or_404(AmortizationSchedule, pk=installment_id)
        initial['amortization_schedule'] = schedule
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule = get_object_or_404(AmortizationSchedule, pk=self.kwargs['pk'])
        context['installment'] = schedule
        context['credit'] = schedule.credit
        return context

    def form_valid(self, form):
        # Verificar que la cuota aún esté pendiente
        schedule = form.cleaned_data['amortization_schedule']
        if schedule.status != AmortizationSchedule.Status.PENDING:
            messages.error(self.request, 'Esta cuota ya fue pagada o está vencida (pero ya tiene un pago registrado).')
            return self.form_invalid(form)

        # Verificar que el monto pagado sea igual al valor de la cuota (sin pagos parciales en MVP)
        amount = form.cleaned_data['amount_paid']
        if amount != schedule.installment_value:
            messages.error(self.request, f'El monto debe ser exactamente el valor de la cuota: ${schedule.installment_value}')
            return self.form_invalid(form)

        # Guardar el pago (el método save() del modelo actualiza cuota y crédito)
        response = super().form_valid(form)
        messages.success(self.request, 'Pago registrado exitosamente.')
        return response

    def get_success_url(self):
        # Redirigir al detalle del crédito asociado
        return reverse('credits:credit_detail', kwargs={'pk': self.object.amortization_schedule.credit.pk})