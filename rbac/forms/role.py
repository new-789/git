

from django import forms
from rbac import models


class RoleModelForm(forms.ModelForm):
    """
    自定义 Form 类 继承 ModelForm 类
    该方法可自动读取出指定 models 模型中创建数据表类名数据库中的所有数据
    model 为执行的数据库表名(即 models 中创建数据库时定义的类名)
    fields 即为指定以列表的形式读取的字段名： “__all__” 表示读取所有
    """
    class Meta:  # 固定语法
        model = models.Role  # 对应 models 中的 role 类
        fields = ['role',]  # 读取出 Role 表中的 role 字段的数据
        widgets = {  # 给读出的字段添加格式语法
            'role': forms.TextInput(attrs={
                                            'class':'form-control',
                                            'placeholder':'请输入需要添加的角色名'
                                            })
                                          }