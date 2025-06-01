from django.urls import path
from . import views
from .views import BoarderDeleteView

urlpatterns = [
    path('', views.boarder_list, name='boarder-list'),
    path('add/', views.add_boarder, name='add-boarder'),
    path('edit/<int:pk>/', views.edit_boarder, name='edit-boarder'),
    path('delete/<int:pk>/', BoarderDeleteView.as_view(), name='delete-boarder'),
]