from django.urls import path
from . import views

urlpatterns = [
    path('doctors', views.doctors, name='doctors'),
    path('department', views.department, name='department'),
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/update/<int:booking_id>/<str:status>/', views.update_appointment_status, name='update_appointment_status'),
    path('dashboard/schedule/', views.manage_schedule, name='manage_schedule'),
    path('dashboard/schedule/delete/<int:avail_id>/', views.delete_availability, name='delete_availability'),
]
