from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

class Client(models.Model):
    """
    Almacena la información de un cliente.
    """
    first_name = models.CharField('nombre(s)', max_length=100)
    last_name = models.CharField('apellidos', max_length=100)
    document_type = models.CharField('tipo de documento', max_length=20, default='CC')
    document_number = models.CharField(
        'número de documento',
        max_length=20,
        unique=True,
        validators=[RegexValidator(r'^\d+$', 'Solo se permiten números.')]
    )
    email = models.EmailField('correo electrónico', unique=True)
    phone = models.CharField('teléfono', max_length=15, blank=True)
    monthly_income = models.DecimalField(
        'ingresos mensuales',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    address = models.TextField('dirección', blank=True)
    created_at = models.DateTimeField('fecha de registro', auto_now_add=True)
    updated_at = models.DateTimeField('última actualización', auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name} - {self.document_number}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"