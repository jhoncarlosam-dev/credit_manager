from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users.views import dashboard


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # Aquí luego incluiremos las URLs de las apps (clientes, créditos, etc.)
    path('', dashboard, name='dashboard'),
    path('clients/', include('clients.urls')),
    path('credits/', include('credits.urls')),
    path('payments/', include('payments.urls'))
]