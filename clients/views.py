from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Client
from django.db import models

class AnalystRequiredMixin(UserPassesTestMixin):
    """Mixin que permite acceso solo a usuarios del grupo 'analyst' o superuser."""
    def test_func(self):
        return self.request.user.groups.filter(name='analyst').exists() or self.request.user.is_superuser

# Vista para listar clientes (accesible por cualquier usuario autenticado)
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(document_number__icontains=search)
            )
        return queryset

# Vista detalle (cualquier usuario autenticado puede ver)
class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'

# Crear cliente (solo analyst)
class ClientCreateView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = Client
    fields = ['first_name', 'last_name', 'document_type', 'document_number', 'email', 'phone', 'monthly_income', 'address']
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

# Actualizar cliente (solo analyst)
class ClientUpdateView(LoginRequiredMixin, AnalystRequiredMixin, UpdateView):
    model = Client
    fields = ['first_name', 'last_name', 'document_type', 'document_number', 'email', 'phone', 'monthly_income', 'address']
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

# Eliminar cliente (solo analyst)
class ClientDeleteView(LoginRequiredMixin, AnalystRequiredMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')