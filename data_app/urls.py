from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-entry/', views.add_entry, name='add_entry'),
    path('test-supabase/', views.test_supabase, name='test_supabase'),
    path('api/entries/', views.list_entries_api, name='list_entries_api'),
]