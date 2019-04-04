from django import forms
from django.core.exceptions import ValidationError  # 导入钩子抛出异常方法
from django.utils.module_loading import import_string
from django.conf import settings
from rbac import models
from rbac.forms.base import BootStrapModelForm  # 导入自编译设置样式基类


class UserModelForm(BootStrapModelForm):
    """
    添加用户自定义 ModelForm 类
    """
    # 自定义字段方法
    confirm_password = forms.CharField(label='确认密码')

    class Meta:
        model = models.UserInfo
        fields = ['username', 'password', 'confirm_password', 'email', ]

    # 自定义钩子函数方法用来校验两次输入的密码是否一致，必须以 clean 开头，
    # 后面的内容则为需要校验的字段
    def clean_confirm_password(self):
        """
        输入的两次密码校验钩子
        :return:
        """
        # 获取两次输入的密码值，即获取在 input 标签中输入的内容
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            # ModelForm 方法中抛出异常语法
            raise ValidationError('输入的两次密码不一致')
        return confirm_password

"""
ModelForm 自定义错误信息方法
        方法一：使用 error_messages 手动自定义错误信息显示内容，
               required 表示该字段为不能为空
          error_messages = {
              'username': {'required': '用户名不能为空'},
              'password': {'required': '密码不能为空'},
              'confirm_password': {'required': '确认密码不能为空'},
              'email': {'required': '邮箱不能为空'},
          }
        方法二：使用 django 提供的翻译功能让其显示中文的错误信息
               在 settings 全局配置文件中将 LANGUAGE_CORE = 'en-us' 改为
               LANGUAGE_CORE = 'zh-hans'  即可

ModelForm 自定义 input 标签样式方法：
    方法一：使用 widgets 手动自定义格式，方法如下：
        widgets = {  # 给读出的字段添加格式语法
            'role': forms.TextInput(attrs={
                                'class':'form-control',
                                'placeholder':'请输入需要添加的角色名'
                            }）
            缺点：字段太多需一个个的书写，且还不支持自定义字段
    方法二：建一个自定义类的初始化方法 __iuit__(self, *args, **kwargs) 
           且继承 ModelForm 方法的 __init__ 方法，并在其中循环从数据库或
           自定义字段的名称及 filed 进行统一设置样式
           代码：
                # 创建 __init__ 方法并继承 ModelForm 的初始化方法
                def __init__(self, *args, **kwargs):
                    super(UserModelForm, self).__init__(*args, **kwargs)
                    # 循环获取的每一个字段名称并依次进行设置样式
                    for name, field, in self.fields.items():
                        field.widget.attrs['class'] = 'form-control'
"""


class UpdateUserModelForm(BootStrapModelForm):
    """
    用户编辑自定义 ModelForm 类
    """
    class Meta:
        user_model_class = import_string(settings.RBAC_USER_MODEL_CLASS)
        model = user_model_class
        fields = ['username', 'email','phone', ]


class ResetPasswordUserModelForm(BootStrapModelForm):
    """
    重置密码自定义 ModelForm 类
    """
    confirm_password = forms.CharField(label='确认密码')
    class Meta:
        model = models.UserInfo
        fields = ['password', 'confirm_password', ]

    def clean_confirm_password(self):
        """
        两次输入的密码校验钩子
        :return:
        """
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise ValidationError('两次输入的密码不一致')
        return confirm_password