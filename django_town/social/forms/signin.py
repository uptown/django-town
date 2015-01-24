from django import forms


class SignInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(min_length=6)