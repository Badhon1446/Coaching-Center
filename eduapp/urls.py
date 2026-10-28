from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('register/',views.registration, name='register'),
    path('login/',views.auth_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('dashboard/',views.dashboard, name='dashboard'),

    #teacher side urls
    path('teacher-dashboard/',views.teacher_dashboard,name='teacher_dashboard'),
    path('create-task',views.create_task, name='create_task'),
    path('details-teacher-task/<int:id>/',views.details_teacher_task,name='details_teacher_task'),
    path('delete-task/<int:id>/',views.delete_task,name='delete_task'),
    path('update-task/<int:id>/',views.update_task,name='update_task'),
    path('result/', views.select_task, name='select_task'),
    path('result/<int:task_id>/', views.add_result, name='add_result'),
    path('teacher/task_submission/<int:task_id>/',views.show_task_submission,name='show_task_submission'),
    path('teacher/add-resource/', views.add_resource, name='add_resource'),

    #student side urls
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('my-task/', views.show_task, name='show_task'),
    path('my-result/', views.show_result, name='show_result'),
    path('task/<int:task_id>/issue/', views.submit_task_issue, name='submit_task_issue'),
    path('task-submit/<int:id>/', views.submit_task,name='submit_task'),
    path('task-details/<int:id>/',views.task_details_std,name='task_details_std'),
    path('student/my-library/', views.my_library, name='my_library'),


]
