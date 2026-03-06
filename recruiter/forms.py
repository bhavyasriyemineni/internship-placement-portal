from django import forms
from .models import RecruiterProfile

class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = '__all__'
        widgets = {
            'industry': forms.TextInput(attrs={
                'placeholder': 'e.g. Software, Finance, Manufacturing'
            }),
        }
