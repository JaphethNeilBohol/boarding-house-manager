from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False), name='home_redirect'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tenants/', views.tenant_list, name='tenant_list'),
    path('tenants/add/', views.tenant_add, name='tenant_add'),
    path('tenants/<int:tenant_id>/edit/', views.tenant_edit, name='edit_tenant'),
    path('tenants/<int:tenant_id>/remove/', views.tenant_remove, name='remove_tenant'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/add/', views.payment_add, name='payment_add'),
    path('payments/edit/<int:payment_id>/', views.payment_edit, name='payment_edit'),
    path('history/', views.history_log, name='history_log'),
    path('logout/', views.logout_view, name='logout'),
    path('rooms/', views.room_list, name='room_list'),
]

