from django import forms
from .models import TaskSubmissions

class TaskSubmissionForm(forms.ModelForm):
    class Meta:
        model = TaskSubmissions
        fields = ['upload','note']

        