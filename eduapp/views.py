from django.shortcuts import render,get_object_or_404,redirect
from .models import AuthUser,Subject,Batch,Teacher,Task,Course,BatchSubject,Result,TaskIssu,TaskSubmissions,Resource
from django.contrib import messages
from django.contrib.auth import login as user_login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .form import TaskSubmissionForm
from django.db.models import Count
from django.core.exceptions import ValidationError
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

        user_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        request.session.set_expiry(86400 * 7)
        messages.success(request, 'Login success!')
        return redirect('home')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

def home(request):
    return render(request,'home.html')


#dashboard_related

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
def student_dashboard(request):
    if  hasattr(request.user, 'teacher'):
        return redirect('home')
    user = request.user
    tasks = Task.objects.filter(batch=user.batch)
    results = Result.objects.filter(task__batch=user.batch, student=user)
    return render(request, 'student_dashboard.html', {
        'tasks': tasks,
        'results': results,
    })



#task_related


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
        add_file = request.FILES.get('add_file')

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
            add_file = add_file,
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
def submit_task(request, id):
    user = request.user
    task = get_object_or_404(Task, id=id, batch=user.batch)
    submission = TaskSubmissions.objects.filter(
        student=user,
        task=task
    ).first()

    if request.method == 'POST':
        form = TaskSubmissionForm(request.POST,request.FILES,instance=submission)
        if form.is_valid():
            answer = form.cleaned_data.get('answer')
            upload = form.cleaned_data.get('upload')

            if not (answer and answer.strip()) and not upload:
                messages.error(request, 'Please write an answer or upload a file.')
            else:
                submit = form.save(commit=False)
                submit.student = user
                submit.task = task
                submit.save()
                messages.success(request, 'Your task has been submitted successfully!')
                return redirect('task_details_std', id=task.id)
        else:
            messages.error(request, 'Please check the submission.')
    else:
        form = TaskSubmissionForm(instance=submission)

    return render(request, 'task_submission.html', {
        'task': task,
        'student': user,
        'form': form,
        'submission': submission,
    })


@login_required
@require_POST
def submit_task_issue(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    text = request.POST.get('issu', '').strip()
    if not text:
        messages.error(request, 'Please write your issue first.')
    else:
        TaskIssu.objects.create(task=task, student=request.user, issu=text)
        messages.success(request, 'Your issue has been sent to the teacher.')
    # je page theke submit korechho sekhanei ferot jabe
    return redirect(request.META.get('HTTP_REFERER') or 'student_dashboard')

@login_required
def select_task(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    tasks = (Task.objects.filter(assign_teacher=teacher)
             .select_related('batch', 'subject')
             .annotate(result_count=Count('result_task', distinct=True))
             .order_by('dateline'))
    return render(request, 'select_task.html', {'tasks': tasks})



def student_tasks(user):
    return (Task.objects.filter(batch=user.batch)
            .select_related('subject').order_by('-dateline'))

@login_required
def show_task(request):
    if hasattr(request.user, 'teacher'):
        return redirect('home')
    return render(request, 'show_task.html', {'tasks': student_tasks(request.user)})


@login_required
def task_details_std(request,id):
    if hasattr(request.user, 'teacher'):
        return redirect('home')
    task = get_object_or_404(Task,id=id)
    return render(request,'task_details_std.html',{'task':task})

# @login_required
# def show_task_submission(request):
#     teacher = request.user.teacher
#     task_submission = TaskSubmissions.objects.filter( task__assign_teacher=teacher).select_related(
#         'student', 'task', 'task__subject').order_by('-submited_at')
    
#     return render(request,'show_task_submission.html',{'task_submission':task_submission})

@login_required
def show_task_submission(request, task_id):
    teacher = get_object_or_404(Teacher, user=request.user)
    task = get_object_or_404(Task,id=task_id,assign_teacher=teacher)
    submissions = TaskSubmissions.objects.filter( task=task).select_related(
        'student', 'task', 'task__subject').order_by('-submited_at')
    
    return render(request, 'teacher_check_answers.html', {'task': task,'submissions': submissions,})



@login_required
def add_result(request,task_id):
    teacher = get_object_or_404(Teacher,user=request.user)
    task = get_object_or_404(Task,id=task_id,assign_teacher=teacher)
    students = AuthUser.objects.filter(batch=task.batch,is_active=True).order_by('id')

    if request.method == 'POST':
        for student in students:
            marks = request.POST.get(f'marks_{student.id}')

            if marks:
                Result.objects.update_or_create(
                    student=student,
                    task=task,
                    defaults={
                        'marks':marks,
                        'assign_teacher':teacher,
                    },
                    )
        messages.success(request, "Result saved!")
        return redirect('add_result', task_id=task.id)

    existing = {r.student_id: r for r in Result.objects.filter(task=task)}
    rows = [{'student': s, 'result': existing.get(s.id)} for s in students]

    return render(request, 'add_result.html', {'task': task, 'rows': rows})


@login_required
def show_result(request):
    results = (Result.objects.filter(student=request.user)
               .select_related('task', 'task__subject', 'task__batch').order_by('-created_at'))
    return render(request, 'show_result.html', {'results': results})

#resource_related

@login_required
def add_resource(request):
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Only teachers can add resources.')
        return render(request, 'add_resource.html')

    teacher = request.user.teacher
    batches = Batch.objects.filter(assign_teacher=teacher)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        resource_type = request.POST.get('resource_type')
        batch_id = request.POST.get('batch')
        file = request.FILES.get('file')
        video_file = request.FILES.get('video_file')
        video_url = request.POST.get('video_url', '').strip()

        if not title or not batch_id:
            messages.error(request, 'Title and batch are required.')
        elif resource_type not in dict(Resource.RESOURCE_TYPES):
            messages.error(request, 'Please select a valid resource type.')
        else:
            batch = batches.filter(pk=batch_id).first()

            if not batch:
                messages.error(request, 'Please select a batch assigned to you.')
            elif resource_type in ['lecture_sheet', 'documentation'] and not file:
                messages.error(request, 'Please upload a document.')
            elif resource_type == 'video' and bool(video_file) == bool(video_url):
                messages.error(request, 'Upload a video or provide a video URL, not both.')
            elif video_file and video_file.size > 20 * 1024 * 1024:
                messages.error(request, 'Video size cannot exceed 20 MB. Please provide a video URL instead.')
            else:
                resource = Resource(
                    title=title,
                    description=description,
                    resource_type=resource_type,
                    file=file if resource_type in ['lecture_sheet', 'documentation'] else None,
                    video_file=video_file if resource_type == 'video' else None,
                    video_url=video_url if resource_type == 'video' and video_url else None,
                    teacher=request.user,
                    batch=batch
                )

                try:
                    resource.full_clean()
                    resource.save()
                    messages.success(request, 'Resource added successfully.')
                except (ValidationError, ValueError) as error:
                    messages.error(request, str(error))

    return render(request, 'add_resource.html', {
        'batches': batches
    })


@login_required
def teacher_show_resource(request):
    resources = Resource.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request,'teacher_show_resource.html',{'resources': resources})

@login_required
@require_POST
def delete_resource(request, id):
    resource = get_object_or_404(Resource,id=id,teacher=request.user)
    resource.delete()
    return redirect('teacher_show_resource')




@login_required
def my_library(request):
    # if not hasattr(request.user, 'student'):
    #     messages.error(request, 'Only student can view resources.')
    #     return render(request, 'my_library.html')
    resources = Resource.objects.filter( batch=request.user.batch
    ).select_related('teacher', 'batch').order_by('-created_at')

    return render(request, 'my_library.html', {
        'resources': resources
    })