from django import forms
from models import *
from django.forms.extras.widgets import SelectDateWidget



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nick_name', 'school', 'profile_image']


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name']


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ['students']

    def clean_section(self):
        cleaned_data = super(CourseForm, self).clean()
        if Course.objects.filter(course_number=self.cleaned_data['course_number']) > 0:
            if Course.objects.get(course_number=self.cleaned_data['course_number']).section == \
                    cleaned_data['section']:
                return False

        return True


class DeadlineForm(forms.ModelForm):
    class Meta:
        model = Deadline
        exclude = ['students']
        widgets = {'due': SelectDateWidget}


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['timestamp']


class RegistrationForm(forms.Form):
    # TODO: form attrs
    username = forms.CharField(max_length=30, label='username', widget=forms.TextInput())
    email = forms.EmailField(max_length=100, label='email', widget=forms.EmailInput())
    password1 = forms.CharField(max_length=30, label='password1', widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=30, label='password2', widget=forms.PasswordInput())

    nick_name = forms.CharField(max_length=30, label='nickname', widget=forms.TextInput())
    school = forms.ModelChoiceField(queryset=School.objects.all())

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two passwords doesn't match.")
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("The username is occupied, please try another one.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact=email):
            raise forms.ValidationError("This email is occupied.")

        return email

        # TODO: clean school

