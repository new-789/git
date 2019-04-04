# -*- coding:utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe
from rbac import models
from rbac.forms.base import BootStrapModelForm  # 导入自编译设置样式基类

# 添加菜单使用的图标内容
ICON_LIST = [
['fa-handshake-o',mark_safe('<i class="fa fa-handshake-o" aria-hidden="true"></i>')],
['fa-institution',mark_safe('<i class="fa fa-institution" aria-hidden="true"></i>')],
['fa-id-badge',mark_safe('<i class="fa fa-id-badge" aria-hidden="true"></i>')],
['fa-desktop',mark_safe('<i class="fa fa-desktop" aria-hidden="true"></i>')],
['fa-address-book',mark_safe('<i class="fa fa-address-book" aria-hidden="true"></i>')],
['fa-address-book-o',mark_safe('<i class="fa fa-address-book-o" aria-hidden="true"></i>')],
['fa-bicycle',mark_safe('<i class="fa fa-bicycle" aria-hidden="true"></i>')],
['fa-blind',mark_safe('<i class="fa fa-blind" aria-hidden="true"></i>')],
['fa-life-ring',mark_safe('<i class="fa fa-life-ring" aria-hidden="true"></i>')],
['fa-plus-circle',mark_safe('<i class="fa fa-plus-circle" aria-hidden="true"></i>')],
['fa-paper-plane',mark_safe('<i class="fa fa-paper-plane" aria-hidden="true"></i>')],
['fa-star',mark_safe('<i class="fa fa-star" aria-hidden="true"></i>')],
['fa-tree',mark_safe('<i class="fa fa-tree" aria-hidden="true"></i>')],
['fa-window-maximize',mark_safe('<i class="fa fa-window-maximize" aria-hidden="true"></i>')],
['fa-user-circle-o',mark_safe('<i class="fa fa-user-circle-o" aria-hidden="true"></i>')],
['fa-thumbs-down',mark_safe('<i class="fa fa-thumbs-down" aria-hidden="true"></i>')],
['fa-thumbs-up',mark_safe('<i class="fa fa-thumbs-up" aria-hidden="true"></i>')],
['fa-server',mark_safe('<i class="fa fa-server" aria-hidden="true"></i>')],
['fa-snowflake-o',mark_safe('<i class="fa fa-snowflake-o" aria-hidden="true"></i>')],
['fa-sign-language',mark_safe('<i class="fa fa-sign-language" aria-hidden="true"></i>')],
['fa-smile-o',mark_safe('<i class="fa fa-smile-o" aria-hidden="true"></i>')],
['fa-power-off',mark_safe('<i class="fa fa-power-off" aria-hidden="true"></i>')],
['fa-question-circle',mark_safe('<i class="fa fa-question-circle" aria-hidden="true"></i>')],
['fa-print',mark_safe('<i class="fa fa-print" aria-hidden="true"></i>')],
['fa-registered',mark_safe('<i class="fa fa-registered" aria-hidden="true"></i>')],
['fa-pencil-square-o',mark_safe('<i class="fa fa-pencil-square-o" aria-hidden="true"></i>')],
['fa-globe',mark_safe('<i class="fa fa-globe" aria-hidden="true"></i>')],
['fa-file-excel-o',mark_safe('<i class="fa fa-file-excel-o" aria-hidden="true"></i>')],
['fa-folder-o',mark_safe('<i class="fa fa-folder-o" aria-hidden="true"></i>')],
['fa-folder-open',mark_safe('<i class="fa fa-folder-open" aria-hidden="true"></i>')],
['fa-envelope-o',mark_safe('<i class="fa fa-envelope-o" aria-hidden="true"></i>')],
['fa-cloud-download',mark_safe('<i class="fa fa-cloud-download" aria-hidden="true"></i>')],
['fa-cloud-upload',mark_safe('<i class="fa fa-cloud-upload" aria-hidden="true"></i>')],
]


class MenuModelForm(forms.ModelForm):
    """
    二级菜单展示 ModelForm
    """
    class Meta:
        model = models.Menu
        fields = ['title', 'icon']
        error_messages = {
            'icon':{'required':'请选择一款图标作为当前菜单的图标'}
        }
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control'}),
            # 设置 input 标签框为 radio 可选择类型的标签，choices=[] 即为提供的选择项
            'icon':forms.RadioSelect(choices=ICON_LIST,attrs={'class':'clearfix'})
        }


class SecondMenuModelForm(BootStrapModelForm):
    """
    二级菜单添加ModelForm
    """
    class Meta:
        model = models.Permission
        exclude = ['ppid']  # exclude 表示去掉某一个字段，其余的全部取出


class PermissionModelForm(BootStrapModelForm):
    """
    权限添加自定义 ModelForm 类
    """
    class Meta:
        model = models.Permission
        fields  = ['title', 'url_alias', 'url', ]


class MultiAddPermissionForm(forms.Form):
    """
    自定义批量增加 form
    """
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    url = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    # 此处 url_alias 原为 name 有错误则改回
    url_alias = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    menu_p_id = forms.ChoiceField(choices=[(None, '--------')],
                          widget=forms.Select(attrs={'class': 'form-control'}),
                          required=False  # 表示可以为空
                               )
    ppid_id = forms.ChoiceField(choices=[(None, '--------')],
                                widget=forms.Select(attrs={'class':'form-control'}),
                                required=False,
                                )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 拼接菜单表及权限表中的字段
        self.fields['menu_p_id'].choices += models.Menu.objects.values_list('id', 'title')
        self.fields['ppid_id'].choices += models.Permission.objects.filter(ppid__isnull=True).exclude(
            menu_p__isnull=True).values_list('pid', 'title')


class MultiEditPermissionForm(forms.Form):
    """
    自定义批量编辑 form
    """
    pid = forms.IntegerField(widget=(
        forms.HiddenInput()
    ))
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    url = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    url_alias = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    menu_p_id = forms.ChoiceField(choices=[(None, '--------')],
                          widget=forms.Select(attrs={'class': 'form-control'}),
                          required=False  # 表示可以为空
                               )
    ppid_id = forms.ChoiceField(choices=[(None, '--------')],
                                widget=forms.Select(attrs={'class':'form-control'}),
                                required=False,
                                )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 拼接菜单表及权限表中的字段
        self.fields['menu_p_id'].choices += models.Menu.objects.values_list('id', 'title')
        self.fields['ppid_id'].choices += models.Permission.objects.filter(ppid__isnull=True).exclude(
            menu_p__isnull=True).values_list('pid', 'title')