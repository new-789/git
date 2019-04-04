# -*- coding:utf-8 -*-
# 统一设置 input 标签样式的基类

from django import forms


class BootStrapModelForm(forms.ModelForm):
    """
    统一设置 input 标签样式的基类
    """

    # 创建 __init__ 方法并继承 ModelForm 的初始化方法
    def __init__(self, *args, **kwargs):
        super(BootStrapModelForm, self).__init__(*args, **kwargs)
        # 循环获取的每一个字段名称并依次进行设置样式
        for name, field, in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
