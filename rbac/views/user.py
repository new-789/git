# -*- coding:utf-8 -*-
"""
用户管理功能视图
"""

from django.shortcuts import render, reverse, HttpResponse, redirect
from rbac import models
from rbac.forms.user import UserModelForm, \
    UpdateUserModelForm, ResetPasswordUserModelForm


def user_list(request):
    """
    用户列表管理功能视图函数
    :param request:
    :return:
    """
    user_queryset = models.UserInfo.objects.all()
    return render(request, 'rbac/user_list.html', {'users': user_queryset})


def user_add(request):
    """
    添加用户功能视图函数
    :param request:
    :return:
    """
    if request.method == "GET":
        form = UserModelForm()
        return render(request, 'rbac/change.html', {'form':form})
    # ModelForm 获取 request.POST 请求中的数据并提交到后台进行校验
    form = UserModelForm(data=request.POST)
    # is_valid() 为校验成功后保存的所有数据，此处判断 is_valid 中是否有值，有值成功则保存
    if form .is_valid():
        form.save()  # 直接将数据保存到数据库表中
        # reverse 说明: 从urls路由控制器中指定的别名反向生成路径(url)地址
        return redirect(reverse('user_list'))
    # 判断出错则返回错误信息，form 中保存了正确的内容及错误信息内容，所以直接返货 form 即可
    return render(request, 'rbac/change.html', {'form': form})


def user_edit(request, id):
    """
    用户编辑功能视图函数
    :param request:
    :param id: 当前用户的 id 号
    :return:
    """
    obj = models.UserInfo.objects.filter(uid=id).first()
    if not obj:
        return render(request, 'rbac/user_error.html')
    if request.method == 'GET':
        form = UpdateUserModelForm(instance=obj)  # instance= 表示给模板传默认值
        return render(request, 'rbac/change.html', {'form':form})
    form = UpdateUserModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse("user_list"))
    return render(request, 'rbac/change.html', {'form': form})


def user_reset_pwd(request, id):
    """
    重置用户密码功能视图函数
    :param request:
    :param id:
    :return:
    """
    obj = models.UserInfo.objects.filter(uid=id).first()
    if not obj:
        return render(request, 'rbac/user_error.html')
    if request.method == 'GET':
        form = ResetPasswordUserModelForm()
        return render(request, 'rbac/change.html', {'form': form})
    form = ResetPasswordUserModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse("user_list"))
    return render(request, 'rbac/change.html', {'form': form})


def user_del(request, id):
    """
    用户删除功能视图函数
    :param request:
    :param id: 当前用户的 id 号
    :return:
    """
    origin_url = reverse('user_list')  # 反向生成 url 地址方法
    if request.method == "GET":  # 点击删除判断如果的 get 请求则返回一个删除提示页面
        return render(request, 'rbac/delete.html', {'cancel':origin_url})
    models.UserInfo.objects.filter(uid=id).delete()  # 对数据库进行删除操作
    return redirect(origin_url)