from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='custom_admin_dashboard'),
    path('doctors/', views.manage_doctors, name='manage_doctors'),
    path('doctors/add/', views.add_doctor, name='add_doctor'),
    path('doctors/edit/<int:pk>/', views.edit_doctor, name='edit_doctor'),
    path('doctors/delete/<int:pk>/', views.delete_doctor, name='delete_doctor'),
    path('departments/', views.manage_departments, name='manage_departments'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/edit/<int:pk>/', views.edit_department, name='edit_department'),
    path('departments/delete/<int:pk>/', views.delete_department, name='delete_department'),
    path('bookings/', views.manage_bookings, name='manage_bookings'),
    path('bookings/update-status/<int:pk>/<str:status>/', views.update_booking_status, name='admin_update_booking_status'),
]
