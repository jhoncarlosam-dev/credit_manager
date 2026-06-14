from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from clients.models import Client

class Credit(models.Model):
    """
    Representa una solicitud o crédito activo.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        APPROVED = 'approved', 'Aprobado'
        ACTIVE = 'active', 'Activo'
        REJECTED = 'rejected', 'Rechazado'
        PAID_OFF = 'paid_off', 'Pagado'

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='credits')
    amount = models.DecimalField('monto del crédito', max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    term_months = models.PositiveIntegerField('plazo (meses)', validators=[MinValueValidator(1), MaxValueValidator(360)])
    annual_interest_rate = models.DecimalField('tasa de interés anual (%)', max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    start_date = models.DateField('fecha de inicio')
    status = models.CharField('estado', max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Crédito'
        verbose_name_plural = 'Créditos'
        ordering = ['-created_at']

    def __str__(self):
        return f"Crédito #{self.id} - {self.client} - {self.amount}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
           old_status = Credit.objects.get(pk=self.pk).status
        super().save(*args, **kwargs)
        # Generar cuotas solo si el crédito es nuevo y se crea como ACTIVE,
        # O si se actualiza de PENDING a ACTIVE y aún no tiene cuotas
        if (is_new and self.status == self.Status.ACTIVE) or (old_status == self.Status.PENDING and self.status == self.Status.ACTIVE):
            if not self.installments.exists():
              self.generate_amortization_schedule()

    def generate_amortization_schedule(self):
        """
        Genera la tabla de amortización (sistema francés) y guarda cada cuota.
        """
        from credits.models import AmortizationSchedule  # Evitar import circular
        from decimal import Decimal
        from dateutil.relativedelta import relativedelta

        # 1. Calcular cuota mensual fija (P * i * (1+i)^n) / ((1+i)^n - 1)
        P = self.amount
        i = (self.annual_interest_rate / Decimal('100')) / Decimal('12')
        n = self.term_months

        if i == 0:
            monthly_payment = P / n
        else:
            monthly_payment = P * (i * (1 + i) ** n) / ((1 + i) ** n - 1)

        monthly_payment = monthly_payment.quantize(Decimal('0.01'))

        # 2. Generar cada cuota
        balance = P
        for num in range(1, n + 1):
            interest = balance * i
            capital = monthly_payment - interest
            if num == n:
                capital = balance  # Ajuste por redondeo
                monthly_payment = interest + capital

            balance -= capital

            due_date = self.start_date + relativedelta(months=num)
            AmortizationSchedule.objects.create(
                credit=self,
                installment_number=num,
                due_date=due_date,
                capital_amount=capital.quantize(Decimal('0.01')),
                interest_amount=interest.quantize(Decimal('0.01')),
                installment_value=monthly_payment.quantize(Decimal('0.01')),
                remaining_balance=balance.quantize(Decimal('0.01')) if balance > 0 else Decimal('0.00'),
                status=AmortizationSchedule.Status.PENDING
            )

class AmortizationSchedule(models.Model):
    """
    Detalle de cada cuota de un crédito.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        PAID = 'paid', 'Pagada'
        OVERDUE = 'overdue', 'Vencida'

    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.PositiveIntegerField('número de cuota')
    due_date = models.DateField('fecha de vencimiento')
    capital_amount = models.DecimalField('monto de capital', max_digits=12, decimal_places=2)
    interest_amount = models.DecimalField('monto de interés', max_digits=12, decimal_places=2)
    installment_value = models.DecimalField('valor de la cuota', max_digits=12, decimal_places=2)
    remaining_balance = models.DecimalField('saldo pendiente después de esta cuota', max_digits=12, decimal_places=2)
    status = models.CharField('estado', max_length=10, choices=Status.choices, default=Status.PENDING)
    paid_date = models.DateField('fecha de pago', null=True, blank=True)

    class Meta:
        verbose_name = 'Cuota'
        verbose_name_plural = 'Cuotas'
        ordering = ['credit', 'installment_number']
        unique_together = ['credit', 'installment_number']

    def __str__(self):
        return f"Cuota {self.installment_number} - {self.credit}"