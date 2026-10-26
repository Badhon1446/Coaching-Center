from django.contrib import admin
from .models import Subject,Teacher, Batch,Task,Course,AuthUser,BatchSubject,Result,TaskIssu,TaskSubmissions
# Register your models here.

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    exclude = ['create_by']

    def has_add_permission(self, request):
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        obj.create_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user','designation']
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id','title','subject','batch','assign_teacher']
    # prepopulated_fields = {'title':('name',)}
admin.site.register(Batch)
admin.site.register(Course)
# admin.site.register(AuthUser)
@admin.register(AuthUser)
class AuthUserAdmin(admin.ModelAdmin):
    list_display = ['name','batch','email']
admin.site.register(BatchSubject)
admin.site.register(Result)
admin.site.register(TaskIssu)
@admin.register(TaskSubmissions)
class TaskSubmissionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'task', 'submited_at')
    list_filter = ('task', 'submited_at')
    search_fields = ('student__name', 'task__title')
