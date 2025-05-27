from django import forms
from .models import LLMChain


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите ваш email'
    }))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите пароль'
    }))


class LLMChainForm(forms.ModelForm):
    class Meta:
        model = LLMChain
        fields = ['name', 'prompt', 'inputs', 'result_template', 'use_results']
        widgets = {
            'prompt': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
            'inputs': forms.Textarea(attrs={'rows': 10, 'class': 'form-control', 'placeholder': '{ "key": "value" }'}),
            'result_template': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
        }