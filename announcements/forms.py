# announcements/forms.py

from django import forms
from .models import Announcement, Category
from django.contrib.auth.models import User, Group

class AnnouncementForm(forms.ModelForm):
    """
    公告创建和编辑表单
    """
    # 使用ModelMultipleChoiceField来选择用户和用户组
    target_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple, # 可以选择多个用户
        label="指定接收用户"
    )
    target_groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple, # 可以选择多个用户组
        label="指定接收用户组"
    )

    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'category', 'publish_at',
            'target_users', 'target_groups', 'emergency_level'
        ]
        widgets = {
            'publish_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}), # HTML5 datetime-local 输入框
            'content': forms.Textarea(attrs={'rows': 10}), # 增大文本区域
        }
        labels = {
            'title': '标题',
            'content': '内容',
            'category': '分类',
            'publish_at': '计划发布时间',
            'emergency_level': '紧急程度',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为所有字段添加Bootstrap样式类
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateTimeInput)):
                field.widget.attrs['class'] = 'form-control rounded-md shadow-sm'
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs['class'] = 'form-control rounded-md shadow-sm'

        # 将target_users和target_groups的选项显示为更友好的名称
        self.fields['target_users'].queryset = User.objects.all().order_by('username')
        self.fields['target_groups'].queryset = Group.objects.all().order_by('name')
