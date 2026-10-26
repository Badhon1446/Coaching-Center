from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)



class AuthUser(AbstractBaseUser,PermissionsMixin):
    name = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=150)
    phone = models.CharField(max_length=11, blank=True, default="")
    batch = models.ForeignKey('Batch',on_delete=models.SET_NULL,null=True,blank=True,related_name='students')
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    objects = CustomUserManager()
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'User'

class Subject(models.Model):
    name = models.CharField(max_length=250)
    is_active = models.BooleanField(default=False)
    create_by = models.ForeignKey(AuthUser,on_delete=models.CASCADE,related_name='create_sub')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'Subject'

class Batch(models.Model):
    name = models.CharField(max_length=150)
    assign_teacher = models.ManyToManyField('Teacher',related_name='batches',blank=True)
    start_date = models.DateTimeField()
    seat = models.BigIntegerField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def student_count(self):
        return self.students.count()

    def available_seat(self):
        return self.seat - self.student_count()

    def __str__(self):
        return f"{self.name} - {self.available_seat()}"
    class Meta:
        db_table = 'Btach'

class Teacher(models.Model):
    user = models.OneToOneField(AuthUser,on_delete=models.CASCADE,related_name='teacher')
    designation = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name
    class Meta:
        db_table = 'Teacher'

class BatchSubject(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='batch_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='batch_subjects')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='batch_subjects')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.batch} - {self.subject} - ({self.teacher})"
    class Meta:
        db_table = 'BatchSubject'
        unique_together = ('batch', 'subject', 'teacher')

class Course(models.Model):

    # assign_teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE,related_name='course_teacher')
    name = models.CharField(max_length=150)
    batch = models.ManyToManyField(Batch,blank=True)
    seats = models.IntegerField()
    descriptions = models.CharField(max_length=300)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'Course'

class Task(models.Model):
    assign_teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE,related_name='task_teacher')
    title = models.CharField(max_length=300)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch,on_delete=models.CASCADE,related_name='task_batch')
    dateline = models.DateTimeField()
    add_file = models.FileField(upload_to='task/',blank=True,null=True)
    description = models.TextField()

    def __str__(self):
        return self.title
    class Meta:
        db_table = 'Task'

class TaskSubmissions(models.Model):
    student = models.ForeignKey(AuthUser,on_delete=models.CASCADE,related_name='student_submission')
    task = models.ForeignKey(Task,on_delete=models.CASCADE,related_name='submission_task')
    upload = models.FileField(upload_to='submission_answer/',blank=True,null=True)
    answer = models.TextField(blank=True,null=True)
    note = models.CharField(max_length=250,blank=True,null=True)
    submited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.task.title}"
    class Meta:
        db_table = 'Submission'


class TaskIssu(models.Model):
    task = models.ForeignKey(Task,on_delete=models.CASCADE,related_name='task_issu')
    student = models.ForeignKey(AuthUser,on_delete=models.CASCADE,related_name='student_issu')
    issu = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task} - {self.student}"
    class Meta:
        db_table = 'TaskIssu'
    
class Result(models.Model):
    student = models.ForeignKey(AuthUser,on_delete=models.CASCADE,related_name='result')
    task = models.ForeignKey(Task,on_delete=models.CASCADE,related_name='result_task')
    marks = models.DecimalField(max_digits=4, decimal_places=2,default=0)
    assign_teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE,related_name='result_teacher')
    upload_result = models.FileField(upload_to='result/',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.task}, - {self.marks}"
    class Meta:
        db_table = 'Result'     
        unique_together = ('student', 'task')


# class Post(models.Model):
#     title = models.CharField(max_length=250)
