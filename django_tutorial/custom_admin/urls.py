from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='custom_admin_dashboard'),
    
    # Doctor Management
    path('doctors/', views.manage_doctors, name='manage_doctors'),
    path('doctors/add/', views.add_doctor, name='add_doctor'),
    path('doctors/edit/<int:doctor_id>/', views.edit_doctor, name='edit_doctor'),
    path('doctors/delete/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
    
    # Department Management
    path('departments/', views.manage_departments, name='manage_departments'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/edit/<int:dept_id>/', views.edit_department, name='edit_department'),
    path('departments/delete/<int:dept_id>/', views.delete_department, name='delete_department'),
    
    # Contact Messages
    path('messages/', views.manage_messages, name='manage_messages'),
    path('messages/view/<int:message_id>/', views.view_message, name='view_message'),
    path('messages/delete/<int:message_id>/', views.delete_message, name='delete_message'),

    # Doctor Portal
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('booking/status/<int:booking_id>/<str:new_status>/', views.update_booking_status, name='update_booking_status'),
    path('my-schedule/', views.schedule_management, name='schedule_management'),
    path('schedule/delete/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('my-leaves/', views.leave_management, name='leave_management'),
    path('leave/delete/<int:leave_id>/', views.delete_leave, name='delete_leave'),
]
