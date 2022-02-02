from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class FileForm(forms.Form):
    file = forms.FileField()


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=200)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = User.objects.filter(username=username)
        if not user:
            raise forms.ValidationError("This user does not exist")
        elif username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Incorrect Password")
            if not user.is_active:
                raise forms.ValidationError("User is not Active")

        return super(UserLoginForm, self).clean(*args, **kwargs)


class CreateUser(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        users = User.objects.all()
        email_qs = users.filter(email=email)
        if email_qs:
            self.errors['email'] = self.error_class(["This email is already registered"])
        return super(CreateUser, self).clean(*args, **kwargs)
