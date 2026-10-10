from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('register/',views.registration, name='register'),
    path('login/',views.auth_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('dashboard/',views.dashboard, name='dashboard'),

    path('teacher-dashboard/',views.teacher_dashboard,name='teacher_dashboard'),
    path('student-dashboard/',views.student_dashboard,name='student_dashboard'),

    path('create-task',views.create_task, name='create_task'),
    path('details-teacher-task/<int:id>/',views.details_teacher_task,name='details_teacher_task'),
    path('delete-task/<int:id>/',views.delete_task,name='delete_task'),
    path('update-task/<int:id>/',views.update_task,name='update_task'),
]
