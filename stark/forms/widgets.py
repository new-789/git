# -*- coding:utf-8 -*-


from django import forms


class DateTimePickerInput(forms.TextInput):
    """
    重写 django 框架中 forms 组件渲染默认返回的 input 标签文件
    使其变为时间选择器 input 框
    """
    template_name = 'stark/forms/widgets/datetime_picker.html'