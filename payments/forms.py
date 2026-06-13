from django import forms
from .models import Payment
from credits.models import AmortizationSchedule

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amortization_schedule', 'amount_paid', 'reference_number', 'notes']
        widgets = {
            'amortization_schedule': forms.HiddenInput(),
            'amount_paid': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Comentarios adicionales'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener el valor de la cuota desde el schedule y setearlo como valor inicial del campo amount_paid
        if 'amortization_schedule' in self.data:
            try:
                schedule_id = int(self.data.get('amortization_schedule'))
                schedule = AmortizationSchedule.objects.get(pk=schedule_id)
                self.fields['amount_paid'].initial = schedule.installment_value
            except (ValueError, AmortizationSchedule.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.amortization_schedule:
            self.fields['amount_paid'].initial = self.instance.amortization_schedule.installment_value