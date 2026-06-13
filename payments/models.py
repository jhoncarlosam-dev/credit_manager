from django.db import models
from django.core.validators import MinValueValidator
from credits.models import AmortizationSchedule

class Payment(models.Model):
    """
    Registra el pago de una cuota.
    """
    amortization_schedule = models.OneToOneField(
        AmortizationSchedule,
        on_delete=models.PROTECT,
        related_name='payment',
        verbose_name='cuota'
    )
    payment_date = models.DateField('fecha de pago', auto_now_add=True)
    amount_paid = models.DecimalField('monto pagado', max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    reference_number = models.CharField('número de referencia', max_length=50, blank=True, null=True)
    notes = models.TextField('notas', blank=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Pago de {self.amount_paid} para {self.amortization_schedule}"

    def save(self, *args, **kwargs):
        """Al guardar un pago, actualiza el estado de la cuota y del crédito."""
        super().save(*args, **kwargs)
        # Marcar la cuota como pagada
        schedule = self.amortization_schedule
        schedule.status = AmortizationSchedule.Status.PAID
        schedule.paid_date = self.payment_date
        schedule.save()
        # Verificar si el crédito quedó pagado
        credit = schedule.credit
        remaining_installments = credit.installments.exclude(status=AmortizationSchedule.Status.PAID)
        if not remaining_installments.exists():
            credit.status = Credit.Status.PAID_OFF
            credit.save()