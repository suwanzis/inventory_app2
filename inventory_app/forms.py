# inventory_app2/inventory_app/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile  # 导入 Profile 模型

class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=150)
    email = forms.EmailField(label='邮箱')
    phone_number = forms.CharField(label='手机号', max_length=15)
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('该用户名已被使用，请选择其他用户名。')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册，请使用其他邮箱。')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('两次输入的密码不一致，请重新输入。')
        return password2

    def save(self):
        try:
            username = self.cleaned_data.get('username')
            email = self.cleaned_data.get('email')
            password = self.cleaned_data.get('password1')
            phone_number = self.cleaned_data.get('phone_number')
            user = User.objects.create_user(username=username, email=email, password=password)
            # 创建或更新用户的 Profile 信息
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = phone_number
            profile.save()
            return user
        except Exception as e:
            raise forms.ValidationError(f'注册失败：{str(e)}')