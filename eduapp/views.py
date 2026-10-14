from django.shortcuts import render,get_object_or_404,redirect
from .models import AuthUser,Subject,Batch,Teacher,Task,Course,BatchSubject,Result,TaskIssu
from django.contrib import messages
from django.contrib.auth import login as user_login,logout
from django.contrib.auth.decorators import login_required
# Create your views here.

def registration(request):

    batches = Batch.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        batch_id = request.POST.get('batch')
        address = request.POST.get('address')
        is_active = request.POST.get('checkbox')

        if AuthUser.objects.filter(email=email).exists():
            messages.error(request,'Email allready exists!')
            return render(request,'register.html',{'batches':batches})

        if not password1 == password2:
            messages.error(request,'Password should be same!')
            return render(request,'register.html',{'batches':batches})

        batch = Batch.objects.get(id=batch_id)
        user = AuthUser.objects.create(
            name = name,
            email = email,
            password = password1,
            phone = phone,
            batch = batch,
            address = address,
            is_active = is_active
        )
        user.set_password(password1)
        user.save()
        user_login(request,user)
        messages.success(request,'User created successfully.')
        return redirect('home')

    return render(request,'register.html',{'batches':batches})

def auth_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not AuthUser.objects.filter(email=email).exists():
            messages.error(request, 'Email does not exist!')
            return render(request, 'login.html')

        user = AuthUser.objects.get(email=email)

        if not user.check_password(password):
            messages.error(request, 'Invalid password!')
            return render(request, 'login.html')

        user_login(request, user)
        request.session.set_expiry(86400 * 7)
        messages.success(request, 'Login success!')
        return redirect('home')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

def home(request):
    return render(request,'home.html')


@login_required
def dashboard(request):
    if hasattr(request.user, 'teacher'):
        return redirect('teacher_dashboard')
    return redirect('student_dashboard')


@login_required
def teacher_dashboard(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('home')

    teacher = request.user.teacher
    taskes = Task.objects.filter(assign_teacher=teacher).order_by('-id')
    my_batches = Batch.objects.filter(assign_teacher=teacher)
    my_subjects = Subject.objects.filter(batch_subjects__teacher=teacher).distinct()
    issues = TaskIssu.objects.filter(task__in=taskes).select_related('task', 'student', 'task__batch')

    assignments = BatchSubject.objects.filter(teacher=teacher).select_related('subject')
    subject_map = {}
    for a in assignments:
        subject_map.setdefault(a.batch_id, []).append(a.subject)

    batches = []
    for batch in my_batches:
        batches.append({
            'batch': batch,
            'subjects': subject_map.get(batch.id, []),
        })

    return render(request, 'teacher_dashboard.html', {
        'teacher': teacher,
        'batches': batches,
        'taskes': taskes,
        'subjects': my_subjects,
        'issues':issues,
    })

@login_required
def create_task(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('home')

    teacher = request.user.teacher

    if request.method == 'POST':
        title = request.POST.get('title')
        subject_id = request.POST.get('subject')
        batch_id = request.POST.get('batch')
        dateline = request.POST.get('dateline')
        description = request.POST.get('description')

        batch = get_object_or_404(Batch, id=batch_id, assign_teacher=teacher)

        subject = get_object_or_404(
            Subject, id=subject_id,
            batch_subjects__teacher=teacher
        )

        Task.objects.create(
            assign_teacher=teacher,
            title=title,
            subject=subject,
            batch=batch,
            dateline=dateline,
            description=description,
        )

        messages.success(request, 'Task created successfully.')
        return redirect('teacher_dashboard')

    return redirect('teacher_dashboard')


@login_required
def update_task(request, id):
    if not hasattr(request.user, 'teacher'):
        return redirect('home')

    teacher = request.user.teacher
    task = get_object_or_404(Task, id=id, assign_teacher=teacher)

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.dateline = request.POST.get('dateline')
        task.description = request.POST.get('description')
        task.save()
        messages.success(request, 'Task updated successfully.')
    return redirect('teacher_dashboard')


@login_required
def details_teacher_task(request, id):
    if not hasattr(request.user, 'teacher'):
        return redirect('home')
    task = get_object_or_404(Task, id=id, assign_teacher=request.user.teacher)
    return render(request,'teacher_task_details.html',{'task': task})

@login_required
def delete_task(request, id):
    if not hasattr(request.user, 'teacher'):
        return redirect('home')

    if request.method != 'POST':
        return redirect('teacher_dashboard')

    task = get_object_or_404(Task, id=id, assign_teacher=request.user.teacher)
    task.delete()
    messages.success(request, 'Task has been deleted!')

    return redirect('teacher_dashboard')
@login_required
def student_dashboard(request):
    if  hasattr(request.user, 'teacher'):
        return redirect('home')
    user = request.user
    tasks = Task.objects.filter(batch=user.batch)
    results = Result.objects.filter(batch=user.batch)

    return render(request, 'student_dashboard.html', {
        'tasks': tasks,
        'results': results,
    })

@login_required
def submit_task_issue(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    text = request.POST.get('issu','').strip()
    if not text:
        messages.error(request, 'Issue likhte hobe.')
    else:
        TaskIssu.objects.create(task=task, student=request.user, issu=text)
        messages.success(request, 'Tomar issue teacher ke pathano hoyeche.')

    return redirect('student_dashboard')


@login_required
def select_task(request):
    teacher = get_object_or_404(Teacher,user=request.user)
    task = Task.objects.filter(assign_teacher=teacher).select_related('batch','subject').order_by(['dateline'])
    return render(request,'',{'task':task})

@login_required
def add_result(request):
    teacher = get_object_or_404(Teacher,user=request.user)
    task = get_object_or_404(Task,id=task.id,assign_teacher=teacher)
    students = AuthUser.objects.filter(batch=task.batch,is_active=True).order_by(['id'])

    if request.method == 'POST':
        for student in students:
            marks = request.POST.get(f'marks_{student.id}')

            if marks:
                Result.objects.update_or_create(
                    student=student,
                    task=task,
                    defaults={
                        'marsk':marks,
                        'assign_teacher':teacher,
                    },
                    )
        messages.success(request, "Result saved!")
        return redirect('add_result', task_id=task.id)

    existing = {r.student_id: r for r in Result.objects.filter(task=task)}
    rows = [{'student': s, 'result': existing.get(s.id)} for s in students]

    return render(request, '', {'task': task, 'rows': rows})


@login_required
def show_result(request):
    results = (Result.objects.filter(student=request.user)
               .select_related('task', 'task__subject', 'task__batch').order_by('-created_at'))
    return render(request, 'show_result.html', {'results': results})