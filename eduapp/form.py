from django import forms
from .models import TaskSubmissions
from .models import BlogPost, BlogComment

class TaskSubmissionForm(forms.ModelForm):
    class Meta:
        model = TaskSubmissions
        fields = ['answer', 'upload', 'note']


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title','category','excerpt','content','cover_image','status']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 px-4 py-3 focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'placeholder': 'Enter post title'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full rounded-xl border border-slate-300 px-4 py-3 focus:ring-2 focus:ring-emerald-500 focus:outline-none'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border border-slate-300 px-4 py-3 focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'rows': 3,
                'placeholder': 'Write a short description...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border border-slate-300 px-4 py-3 focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'rows': 10,
                'placeholder': 'Write your post...'
            }),
            'cover_image': forms.ClearableFileInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 p-3'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full rounded-xl border border-slate-300 px-4 py-3 focus:ring-2 focus:ring-emerald-500 focus:outline-none'
            })
        }


class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['content']

        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full rounded-xl border border-slate-300 px-4 py-3 focus:ring-2 focus:ring-emerald-500 focus:outline-none',
                'rows': 3,
                'placeholder': 'Write your comment...'
            })
        }
