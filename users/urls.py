from django.urls import path
from .views import login_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', login_views, name='login'),  # ✅ This uses your function
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]