from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, CourseResource,CourseChapter,Activity, CollaborationDiscussion,DiscussionReply, MeetingRecord, Achievement
from django.utils import timezone
# 自定义登录表单
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'}))

# 自定义注册表单
class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '邮箱'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '确认密码'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

# 课时编辑表单
class CourseChapterForm(forms.ModelForm):
    class Meta:
        model = CourseChapter
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '如：01Java概述'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': '排序号，数字越小越靠前'}),
        }
        labels = {
            'title': '课时标题',
            'order': '排序号',
        }

# 资源上传表单
class CourseResourceForm(forms.ModelForm):
    class Meta:
        model = CourseResource
        fields = ['chapter', 'title', 'resource_type', 'file', 'link', 'start_time']
        widgets = {
            'chapter': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '如：JDK下载地址'}),
            'resource_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': '如：https://www.oracle.com/java/'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        labels = {
            'chapter': '所属课时',
            'title': '资源名称',
            'resource_type': '资源类型',
            'file': '上传文件（文件类资源必填）',
            'link': '资源链接（链接类资源必填）',
            'start_time': '开始时间',
        }

    # 表单验证：文件和链接必须填一个
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        link = cleaned_data.get('link')
        resource_type = cleaned_data.get('resource_type')

        if resource_type == 'link' and not link:
            raise forms.ValidationError('链接类资源必须填写资源链接！')
        elif resource_type != 'link' and not file:
            raise forms.ValidationError('非链接类资源必须上传文件！')
        
        return cleaned_data

# 活动表单
class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['title', 'content', 'status', 'start_time', 'end_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

# 协作讨论表单
class CollaborationDiscussionForm(forms.ModelForm):
    class Meta:
        model = CollaborationDiscussion
        fields = ['title', 'content', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# 讨论回复表单
class DiscussionReplyForm(forms.ModelForm):
    class Meta:
        model = DiscussionReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# 会议记录表单
class MeetingRecordForm(forms.ModelForm):
    class Meta:
        model = MeetingRecord
        fields = ['title', 'content', 'meeting_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'meeting_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

# 成果展示表单
class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'content', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }