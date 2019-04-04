# -*- coding:utf-8 -*-

import functools
from types import FunctionType
from django.utils.safestring import mark_safe
from django.db.models import ForeignKey, ManyToManyField
from django.urls import re_path, reverse
from django.shortcuts import HttpResponse, render, redirect
from django.http import QueryDict
from django.db.models import Q
from django import forms
from stark.utils.pagination import Pagination  # 调用自定义分页功能方法类


def get_choices_text(title, field):
    """
    闭包函数：对于 stark 组件中定义列时，choice 如果想要显示中文信息，调用此方法即可
    用来对数据库有 choices 字段自定义函数显示方法对于 choices 字段，如果想获取
    该字段的中文，则使用通过读取数据库内容返回的 queryset列表中的对象.get_字段名_display()
    方法获取到
    :param title: 希望在页面显示的表头
    :param field: 数据库的字段名称
    :return:
    """

    def inner(self, obj=None, is_header=True, *args, **kwargs):
        if is_header:
            return title
        method = "get_%s_display" % field  # 拼接 get_字段名_display 方法
        # getattr(obj,method)() 表示执行使用 obj 对象 get_字段名_display() 方法
        return getattr(obj, method)()

    return inner


def get_datetime_text(title, field, time_format='%Y-%m-%d'):
    """
    闭包函数:
    stark 组件中钩子方法用于对于 django 默认显示时间的修改(即对 django
    默认显示时间的处理做格式化处理，即显示 2000-10-10 时间格式)，
    使用方法：在应用中的 stark 模块中导入该函数并传参，第一个参数为列显示的内容
             第二个参数则为数据库的字段名，第三个参数则为要格式化的时间，需从
             应用中的 stark 模块中导入该函数进行传参
    :param title: 希望在页面显示的表头
    :param field: 数据库的字段名称
    :param time_format: 要格式化的时间,
    :return:
    """

    def inner(self, obj=None, is_header=True, *args, **kwargs):
        if is_header:
            return title
        datetime_value = getattr(obj, field)  # 从函数中获取字段名
        return datetime_value.strftime(time_format)

    return inner


def get_m2m_text(title, field):
    """
    闭包函数：对于 stark 组件中定义列时，显示 M2M 文本信息
    方法获取到
    :param title: 希望在页面显示的表头
    :param field: 数据库的字段名称
    :return:
    """

    def inner(self, obj=None, is_header=True):
        if is_header:
            return title
        queryset = getattr(obj, field).all()  # 从函数中获取字段对象，并获取全部数据
        text_list = [str(row) for row in queryset]
        return ','.join(text_list)  # 对列表中的内容使用 , 号进行拼接

    return inner


class SearchGroupRow():
    """
    对组合搜索获取到的数据进行封装的类，使其返回一个可迭代的对象，
    方便在页面进行循环显示
    """

    def __init__(self, title, queryset_or_tuple, option, query_dict):
        """

        :param title: 组合搜索的列名称
        :param queryset_or_tuple: 组合搜索关联获取到的数据
        :param option: 配置
        :param query_dict: request.GET
        """
        self.queryset_or_tuple = queryset_or_tuple
        self.option = option
        self.title = title
        self.query_dict = query_dict

    def __iter__(self):
        """
        使其返回一个可迭代对象
        :return:
        """
        yield "<div class='whole'>"
        yield self.title + ":"
        yield "</div>"
        yield "<div class='others'>"
        total_query_dict = self.query_dict.copy()
        total_query_dict._mutable = True
        # 获取 request 请求中选择的所有组合搜索文本背后的值(获取到的内容为str类型)
        origin_value_list = self.query_dict.getlist(self.option.field)
        # 判断如果 origin_value_list 中没有数据则表示没有选择按钮应该表示全部选中显示,
        # 如果其中一个没有选择则删除没有选择按钮的参数
        if not origin_value_list:
            yield "<a class='active' href='?%s'>全部</a>" % total_query_dict.urlencode()
        else:
            total_query_dict.pop(self.option.field)
            yield "<a href='?%s'>全部</a>" % total_query_dict.urlencode()
        for item in self.queryset_or_tuple:
            # 获取用户自定义函数中文本内容
            text = self.option.get_text(item)
            # 调用 get_value_func 方法获取组合搜索文本背后的值(id)
            value = str(self.option.get_value_func(item))
            # 将当前请求的 querySet 对象拷贝一份，让其修改里面的内容
            query_dict = self.query_dict.copy()
            query_dict._mutable = True  # 设置 request 的值允许被修改

            # 判断如果 self.option.is_multi 为 True 则表示支持组合搜索多选
            if not self.option.is_multi:
                # 给 querySet 对象中添加属性(即获取到的 id ),用来稍后取出其中的值用来生成 URL
                query_dict[self.option.field] = value
                if value in origin_value_list:
                    # 表示再次点击当前已经选择的按钮则删除当前self.option.field名称的参数
                    query_dict.pop(self.option.field)
                    yield "<a class='active' href='?%s'>%s</a>" % (query_dict.urlencode(), text)
                else:
                    yield "<a href='?%s'>%s</a>" % (query_dict.urlencode(), text)
            else:
                # 获取组合搜索中多选内容背后的值(id)
                multi_value_list = query_dict.getlist(self.option.field)
                # 判断当前点击的按钮的值在 multi_values_list 列表中则表示之前是选中状态则删除当前的值,
                # 不存在则添加,并重新设置 query_dict 中的内容
                if value in multi_value_list:
                    multi_value_list.remove(value)
                    query_dict.setlist(self.option.field, multi_value_list)
                    yield "<a class='active' href='?%s'>%s</a>" % (query_dict.urlencode(), text)
                else:
                    multi_value_list.append(value)
                    query_dict.setlist(self.option.field, multi_value_list)
                    yield "<a href='?%s'>%s</a>" % (query_dict.urlencode(), text)
        yield "</div>"


class Option():

    def __init__(self, field, is_multi=None, db_condition=None, text_func=None, value_func=None):
        """
        组合搜索条件数据封装类，该类可在应用中的 stark 模块中进行重写，
        以达到修改组合搜索条件的目的
        :param field: 组合搜索的字段
        :param is_multi=None: 是否支持多选
        :param db_condition: # 组合搜索数据库过滤的条件
        :param text_func: # 表示用户自定义函数显示内容，用来接收一个函数的值
        """
        self.field = field
        if not db_condition:
            db_condition = {}
        self.db_condition = db_condition
        self.text_func = text_func
        self.is_choices = False  # 用来确定对象是否是 choices 类型
        self.value_func = value_func
        self.is_multi = is_multi

    def get_db_condition(self, request, *args, **kwargs):
        return self.db_condition

    def get_queryset_or_tuple(self, model_class, request, *args, **kwargs):
        """
        根据字段获数据库关联的数据
        :param model_class:
        :param request: 用来接收 URL 传递的参数
        :param args: 用来接收 URL 所带的参数
        :param kwargs: 用来接收 URL 所带的参数
        :return:
        """
        # 根据字符串获取字段对象
        field_object = model_class._meta.get_field(self.field)
        title = field_object.verbose_name  # 获取每个字段定义的 verbose_name 属性的值
        # 判断字段类型是 ForeignKey 或的 ManyToManyField 类型
        if isinstance(field_object, ForeignKey) or isinstance(field_object, ManyToManyField):
            # 对于 FK 和 M2M，应该去获取关联表中的数据，返回 QuerySet 数据类型
            db_condition = self.get_db_condition(request, *args, **kwargs)
            return SearchGroupRow(title, field_object.remote_field.__dict__.get('model').objects.filter(**db_condition),
                                  self, request.GET)
        else:
            self.is_choices = True  # 是 choices 类型的对象则更改 self.choices 的值为 True
            # 获取 choices 中的数据，返回 tuple
            return SearchGroupRow(title, field_object.choices, self, request.GET)

    def get_text(self, field_object):
        """
        获取用户传递的文本函数
        :param field_object:
        :return:
        """
        if self.text_func:  # 如果函数存在则直接返回该函数并执行自定义的函数
            return self.text_func(field_object)
        # 如果 self.choices 的值为 True 则为元组类型的对象，则直接返回元组中的内容，否则返回对象的 str 方法
        if self.is_choices:
            return field_object[1]
        return str(field_object)

    def get_value_func(self, field_object):
        """
        获取文本背后的值(即县级组合搜索条件后的 id)
        :param field_object:
        :return:
        """
        if self.value_func:  # 如果函数存在则直接返回该函数并执行自定义的函数
            return self.text_func(field_object)
        # 如果 self.choices 的值为 True 则为元组类型的对象，则直接返回元组中的内容，否则返回对象的 str 方法
        if self.is_choices:
            return field_object[0]
        return field_object.pk


class StarkModelForm(forms.ModelForm):
    """
    统一设置forms 组件渲染 input 标签样式的基类
    """

    # 创建 __init__ 方法并继承 ModelForm 的初始化方法
    def __init__(self, *args, **kwargs):
        super(StarkModelForm, self).__init__(*args, **kwargs)
        # 循环获取的每一个字段名称并依次进行设置样式
        for name, field, in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class StarkForm(forms.Form):
    """
    自定义 Form 类基类，用来渲染 input 标签样式
    """

    # 创建 __init__ 方法并继承 Form 的初始化方法
    def __init__(self, *args, **kwargs):
        super(StarkForm, self).__init__(*args, **kwargs)
        # 循环获取的每一个字段名称并依次进行设置样式
        for name, field, in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class StarkHandler():
    """
    公共视图函数基类
    """
    list_display = []  # 用于在应用 Handler 子类中重定义该变量，里表中的内容为需要在页面展示的内容字段
    per_page_count = 10  # 默认可显示的每页数据条数，可在各自的类中重写
    has_add_btn = True  # 添加按钮变量，根据此变量显示或影藏按钮，可在子类中重写该变量
    model_from_class = None  # 该变量在判断该变量有值或为空进行用户自定制 modelform 类
    order_list = []  # 默认排序功能用变量，可在每个应用中的 stark 模块中自定义该变量更改排序方法
    search_list = []  # 模糊搜索，可在应用中 stark 模块中重写还变量，列表中的值为需要进行模糊搜索的字段
    action_list = []  # 默认显示下拉框按钮选项的内容，可在应用中自定制白列表中的内容
    search_group = []  # 默认组合搜索需要显示的组合搜索条件，默认为空既没有组合搜索，则在应用中自定义
    # 用于根据需要重定义 html 模板的使用，默认为空，当在应用子类 Handler 中重新定义该变量等于某个模板即可
    change_list_template = None
    add_template = None
    change_template = None
    delete_template = None

    def __init__(self, site, model_class, prev):
        """
        初始化方法
        :param model_class: 接收来自 stark 组件中 v1 类传过来的 model_class
        """
        self.site = site
        self.model_class = model_class
        self.prev = prev
        self.request = None

    ################### 页面内容显示区 #####################
    def get_add_btn(self, request, *args, **kwargs):
        """
        预留钩子做权限的判断是否获取添加按钮并显示，
        可在各自应用继承该父类方法中重写
        :return:
        """
        if self.has_add_btn:
            # 根据别名反向生成 URL
            add_url = self.reverse_add_url(*args, **kwargs)
            return "<a class='btn btn-info' href='%s' " \
                   "style='margin-bottom: 2px; height: 33px;width: 68px;'>" \
                   "    <i class='fa fa-plus'></i> 添加" \
                   "</a>" % add_url
        return None  # 如 has_add_btn 变量为 false 则返货 None 表示不显示按钮

    def get_list_display(self, request, *args, **kwargs):
        """
        预留的自定义扩展，获取页面上显示的列,定义此方法作用在于可以在
        app 应用内的 stark文件中重写 get_list_display 方法，
        以后可根据用户的不同显示不同的列,

        :return:
        """
        value = []
        # 表示设置了 list_display 则默认显示编辑及删除按钮,如想一列显示则值需要添加
        # StarkHandler.display_edit_del 即可，若想双列显示则添加 StarkHandler.display_edit
        # 及 StarkHandler_del 两个内容
        if self.list_display:
            value.extend(self.list_display)
            value.append(type(self).display_edit_del)
        return value

    def display_checkbox(self, obj=None, is_header=None, *args, **kwargs):
        """
        自定义页面显示的列(包括表头和内容),自定义显示 checkbox input 标签
        及反向生成 url
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:  # 判断如果 is_header 为 True 则返回一个选择表头到页面
            return '选择'
        # 注：返回的 a 标签则必须使用 mark_safe 进行包裹
        return mark_safe("<input type='checkbox' name='pk' value='%s' />" % obj.pk)

    def display_edit(self, obj=None, is_header=None, *args, **kwargs):
        """
        自定义页面显示的列(包括表头和内容)
        及反向生成 url
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:  # 判断如果 is_header 为 True 则返回一个编辑的表头到
            return '编辑'
        # 根据别名获取 url 地址，args 为 url 地址中(\d+) 正则匹配内容,并传值
        change_url = self.reverse_change_url(pk=obj.pk)
        # 注：返回的 a 标签则必须使用 mark_safe 进行包裹
        return mark_safe("<a class='fa fa-edit' href='%s'></a>" % change_url)

    def display_del(self, obj=None, is_header=None, *args, **kwargs):
        """
        自定义页面显示的列(包括表头和内容)
        及反向生成 url
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:  # 判断如果 is_header 为 True 则返回一个编辑的表头到
            return '删除'
        del_url = self.reverse_del_url(pk=obj.pk)
        # 注：返回的 a 标签则必须使用 mark_safe 进行包裹
        return mark_safe("<a class='fa fa-trash-o' href='%s'></a>" % del_url)

    def display_edit_del(self, obj=None, is_header=None, *args, **kwargs):
        """
        将编辑和删除操作一列进行显示
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return '选项'
        change_url = self.reverse_change_url(pk=obj.pk)
        del_url = self.reverse_del_url(pk=obj.pk)
        tpl = "<a class='fa fa-edit' href='%s' style='color: blue;'></a>&nbsp;|&nbsp;" \
              "<a class='fa fa-trash-o' href='%s' style='color: red;'></a>" % (change_url, del_url)
        return mark_safe(tpl)

    def get_order_list(self):
        """
        展示列表排序功能方法
        返回的内容语法说明：如果 self.order_list 中有值则返回该变量，
                         没有则返回默认主键(即id)进行排序
        :return:
        """
        """
        下面返回内容语法类似该语法
        if self.order_list:
            return self.order_list
        else:
            ['-pk']
        """
        # 此处用 pk 是为了防止用户表继承 rbac 组件中用户表后在查找数据时，
        # 报无法将关键字解析为字段错误
        return self.order_list or ['-pk']

    def get_search_list(self):
        """
        预留钩子函数方法，方便对搜索的内容进行调整
        :return:
        """
        return self.search_list

    def get_search_group(self):
        """
        组合搜索功能预留钩子函数
        :return:
        """
        return self.search_group

    def get_search_group_condition(self, request):
        """
        获取组合搜索的条件
        :return:
        """
        condition = {}
        # 循环自定义组合搜索列表中的内容
        for option in self.get_search_group():
            # 判断如果支持多选则使用 getlist 获取多列内容 %s__in 过滤条件，
            # 否则直接获取 option.file 字段的值即可等于即可
            if option.is_multi:
                # 获取 request 请求中的所有数据，使用 getlist 是为了可以支持多选
                values_list = request.GET.getlist(option.field)
                if not values_list:
                    continue
                condition['%s__in' % option.field] = values_list
            else:
                value = request.GET.get(option.field)
                if not value:
                    continue
                condition[option.field] = value
        return condition

    def get_action_list(self):
        """
        获取 active_list 列表中的内容即下拉框显示按钮的内容
        :return:
        """
        return self.action_list

    def action_multi_delete(self, request, *args, **kwargs):
        """
        批量删除(如果想要定制执行成功后的返回值，那么就需要为该函数设置返回值)
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()  # 执行批量删除操作

    action_multi_delete.text = '批量删除'  # 给该函数对象使用 text 方法设置一个中文内容用以在页面显示

    #################### 公共视图函数区 ############################
    def get_queryset(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return self.model_class.objects

    def changeList_view(self, request, *args, **kwargs):
        """
        展示列表页面方法
        :param request:
        :return:
        """
        ######################## 1、处理下拉框批量操作 ###################
        action_list = self.get_action_list()
        action_dict = {func.__name__: func.text for func in action_list}
        if request.method == 'POST':
            active_func_name = request.POST.get('active')
            # 判断如果
            if active_func_name and active_func_name in action_dict:
                # 使用映射的方法执行 active_func_name 函数
                active_response = getattr(self, active_func_name)(request, *args, **kwargs)
                # 判断执行删除数据的函数中是否有返回值则执行返回的值，用来做执行完毕后页面跳转或其它操作
                if active_response:
                    return active_response
        """  
        2、模糊搜索功能实现
        1、如果 search_list 列表为空，则不显示搜索框
        2、获取用户提交的关键字,有值则进行筛选
        3、构造搜索条件
        """
        search_list = self.search_list
        search_value = request.GET.get('search', '')
        conn = Q()
        conn.connector = 'OR'  # 定义 Q 对象的查询条件 OR 表示或
        # 判断，如果用户输入搜索框中有值则进行循环定义的搜索条件，并添加到 Q 对象中作为搜索条件
        if search_value:
            for item in search_list:  # 使用 for 循环构造索索条件
                conn.children.append((item, search_value))  # 注
        self.model_class.objects.filter(conn)

        ################### 3、处理排序 ###################
        order_list = self.get_order_list()
        # 获取组合搜索的条件
        search_group_condition = self.get_search_group_condition(request)
        # 将从数据库获取出的内容使用 order_by 方法按照定义的 order_list 中的数据进行排序，
        # 并返回 queryset 对象，方便下面使用该对象继续对会去到的数据进行处理
        prev_queryset = self.get_queryset(request, *args, **kwargs)
        queryset = prev_queryset.filter(conn).filter(**search_group_condition).order_by(*order_list)

        ################### 4、处理分页 ####################
        # 从数据库中获取所有的数据,.count 则为统计出的 querySet 中的总数据
        all_count = queryset.count()
        query_params = request.GET.copy()  # 将 query 请求的地址拷贝一份
        query_params._mutable = True

        pager = Pagination(
            current_page=request.GET.get('page'),
            all_count=all_count,
            base_url=request.path_info,
            query_params=query_params,
            per_page=self.per_page_count,
        )
        data_list = queryset[pager.start:pager.end]

        ################### 5、处理表格 ####################
        # 调用预留钩子方法
        list_display = self.get_list_display(request, *args, **kwargs)
        # 5.1、处理表格的表头
        header_list = []
        if list_display:  # 表示没有定义需要显示的列则直接显示表名
            # 循环每个类中自定义的需要显示的列获取创建数据表时每个字典的 verbose_name 属性
            for key_or_func in list_display:
                # 判断如果该对象如果是函数则执行该函数，并获取函数返回的值
                if isinstance(key_or_func, FunctionType):
                    verbose_name = key_or_func(self, obj=None, is_header=True)
                else:
                    # 循环每个类中自定义的需要显示的列获取创建数据表时每个字典的 verbose_name 属性
                    verbose_name = self.model_class._meta.get_field(key_or_func).verbose_name
                header_list.append(verbose_name)
        else:
            header_list.append(self.model_class._meta.model_name)

        # 5.2、处理表的内容
        # 对数据库中的数据进行切片提取
        body_list = []
        for row in data_list:  # 循环从数据库取出的 quertset 列表对象
            tr_list = []
            # 表示没有定义需要显示的列则直接显示 querytset 列表中的对象，由于在创建了数据表时定义了
            # __str__ 方法所以同样会显示内容
            if list_display:
                for key_or_func in list_display:  # 循环设置列中定义列的数据
                    # 判断如果该对象如果是函数则执行该函数，并获取函数返回的值,添加到 tr_list 中
                    if isinstance(key_or_func, FunctionType):
                        tr_list.append(key_or_func(self, row, is_header=False, *args, **kwargs))
                    else:
                        # 根据设置的列数据获取每个queryset 对象中的内容并添加值列表
                        tr_list.append(getattr(row, key_or_func))
            else:
                tr_list.append(row)
            body_list.append(tr_list)

        ################ 6、处理添加按钮 #####################
        add_btn = self.get_add_btn(request, *args, **kwargs)

        ################ 7、组合搜索 #####################
        search_group_row = []
        search_group = self.get_search_group()
        for option_object in search_group:
            # option_object 即为组合数据搜索封装的类 Option
            row = option_object.get_queryset_or_tuple(self.model_class, request, *args, **kwargs)
            search_group_row.append(row)

        return render(request,
                      # change_list_template 如果为空则使用后面的模板，为真则使用 change_list_template 指定的模板
                      self.change_list_template or 'stark/changelist.html',
                      {'data_list': data_list,
                       'header_list': header_list,
                       'body_list': body_list,
                       'pager': pager,
                       'add_btn': add_btn,
                       'search_list': search_list,
                       'search_value': search_value,  # 用来保存搜索条件
                       'action_dict': action_dict,
                       'search_group_row': search_group_row,
                       }
                      )

    def add_view(self, request, *args, **kwargs):
        """
        添加内容方法
        :param request:
        :return:
        """
        model_form_class = self.get_model_form_class(True, request, None, *args, **kwargs)
        if request.method == 'GET':
            form = model_form_class
            return render(request, self.add_template or 'stark/change.html', {'form': form})
        form = model_form_class(data=request.POST)
        if form.is_valid():
            response = self.save(request, form, False, *args, **kwargs)
            return response or redirect(self.reverse_list_url(*args, **kwargs))

        return render(request,
                      self.add_template or 'stark/change.html',
                      {'form': form})

    def get_change_object(self, request, pk, *args, **kwargs):
        return self.model_class.objects.filter(pk=pk).first()

    def change_view(self, request, pk, *args, **kwargs):
        """
        编辑内容方法
        :param request:
        :return:
        """
        current_change_obj = self.get_change_object(request, pk, *args, **kwargs)
        if not current_change_obj:
            return HttpResponse('要修改的数据不存在，请重新选择')
        model_form_class = self.get_model_form_class(False, request, pk, *args, **kwargs)
        if request.method == 'GET':
            form = model_form_class(instance=current_change_obj)
            return render(request, self.change_template or 'stark/change.html', {'form': form})
        form = model_form_class(data=request.POST, instance=current_change_obj)
        if form.is_valid():
            response = self.save(request, form, True, *args, **kwargs)
            return response or redirect(self.reverse_list_url(*args, **kwargs))
        return render(request,
                      self.change_template or 'stark/change.html',
                      {'form': form})

    def get_delete_object(self, request, pk, *args, **kwargs):
        self.model_class.objects.filter(pk=pk).delete()

    def delete_view(self, request, pk, *args, **kwargs):
        """
        删除内容方法
        :param request:
        :param pk:
        :return:
        """
        origin_list_url = self.reverse_list_url(*args, **kwargs)
        if request.method == 'GET':
            return render(request,
                          self.delete_template or 'stark/delete.html',
                          {'cancel': origin_list_url})
        response = self.get_delete_object(request, pk, *args, **kwargs)
        return response or redirect(origin_list_url)

    ################ 反向生成列表、添加、编辑、删除 URL 内容################
    def reverse_commons_url(self, name, *args, **kwargs):
        """
        反向生成 URL 地址公共方法,当其它功能自定义 URL 后，需要反向生成 URL 时，
        直接调用该方法即可，
        :param name: 为当前 url 设置的 name 别名
        :param args: 用来接收其它参数如 id 主键等等
        :param kwargs:
        :return:
        """
        name = "%s:%s" % (self.site.namespace, name)
        base_url = reverse(name, args=args, kwargs=kwargs)
        if not self.request.GET:  # 判断 request 请求的地址中是否带有参数
            add_url = base_url
        else:
            param = self.request.GET.urlencode()  # 获取 request 请求地址中参数方法
            new_query_dict = QueryDict(mutable=True)  # 设置 QueryDict 对象可修改
            new_query_dict['_filter'] = param
            add_url = "%s?%s" % (base_url, new_query_dict.urlencode())
        return add_url

    def reverse_list_url(self, *args, **kwargs):
        """
        获取页面功能操作完之后返回回相对应列表首页时生成的带原有搜索条件的 url
        :return:
        """
        name = "%s:%s" % (self.site.namespace, self.get_list_url_name)
        base_url = reverse(name, args=args, kwargs=kwargs)
        param = self.request.GET.get('_filter')
        if not param:
            return base_url
        url = "%s?%s" % (base_url, param)
        return url

    def reverse_add_url(self, *args, **kwargs):
        """
        添加页面公共获取反向生成带有原搜索条件的添加 url
        :return:
        """
        return self.reverse_commons_url(self.get_add_url_name, *args, **kwargs)

    def reverse_change_url(self, *args, **kwargs):
        """
        编辑页面公共获取反向生成带有原搜索条件的编辑 url
        :return:
        """
        return self.reverse_commons_url(self.get_change_url_name, *args, **kwargs)

    def reverse_del_url(self, *args, **kwargs):
        """
        删除页面公共获取反向生成带有原搜索条件的删除 url
        :return:
        """
        return self.reverse_commons_url(self.get_delete_url_name, *args, **kwargs)

    ################## 公共 ModelForm 方法区 ####################
    def save(self, request, form, is_update, *args, **kwargs):
        """
        在使用 ModelForm 保存数据数据库之前预留的钩子方法
        作用：如用户在自定义了 modelform 类根据需要显示字段后，而数据库中有的字段又不能为空时，
             则用户可重写该方法，在保存前为不能为空的字段指定一个值
        :param form:
        :param request:
        :param is_update:
        :return:
        """
        form.save()

    def get_model_form_class(self, is_add, request, pk, *args, **kwargs):
        """
        共用 model 类方法。用来做页面渲染操作
        :param is_add: 用来 userinfo 信息添加和编辑页面 model_form 的定制
        :return:
        """
        # 判断如果 model_from_class 如果为 False 则执行应用中自定的 modelform 类，使其可增加字段
        if self.model_from_class:
            return self.model_from_class

        class DynamicModelForm(StarkModelForm):
            class Meta:
                model = self.model_class
                fields = '__all__'

        return DynamicModelForm

    ################## 获取 URL 别名方法区 ######################
    @property
    def get_list_url_name(self):
        """
        获取列表页面 URL 的 name 别名
        调用 get_url_name 公共方法拿到 url 地址
        :return:
        """
        return self.get_url_name('list')

    @property
    def get_add_url_name(self):
        """
        获取添加页面 URL 的 name 别名
        调用 get_url_name 公共方法拿到 url 地址
        :return:
        """
        return self.get_url_name('add')

    @property
    def get_change_url_name(self):
        """
        获取编辑页面 URL 的 name 别名
        调用 get_url_name 公共方法拿到 url 地址
        :return:
        """
        return self.get_url_name('change')

    @property
    def get_delete_url_name(self):
        """
        获取删除页面 URL 的 name 别名
        调用 get_url_name 公共方法拿到 url 地址
        :return:
        """
        return self.get_url_name('delete')

    def wrapper(self, func):
        """
        闭包函数：用于在每次在执行视图函数之前，
        首先给 self.request 进行赋值
        func 用于接收视图函数
        self.wrapper(self.changeList_view) 装饰器的另一种用法，
        及执行完 wrapper 函数中在去执行视图函数
        表示将函数传入该闭包函数中，返回 inner 即执行 wrapper 函数即可
        获取到 inner 函数中的返回的值
        :param func:
        :return:
        """

        @functools.wraps(func)  # 此方法为保留原函数即 func 参数接收     函数的原信息
        def inner(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)

        return inner

    def get_url_name(self, param):
        """
        获取 url 别名公共构造方法，判断 self.prev (后缀)如果存在则加上后缀，
        不存在则直接返回不带后缀的 url
        :param param:
        :return:
        """
        app_label, model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        if self.prev:
            return '%s_%s_%s_%s' % (app_label, model_name, self.prev, param)
        return '%s_%s_%s' % (app_label, model_name, param)

    ################# URL 地址生成区 #############################
    def get_urls(self):
        """
        url 地址生成
        name=self.各自的获取 name 别名构造方法，
        各自获取别名的方法数据来自 get_url_name 构造方法
        :return:
        """
        patterns = [
            re_path(r'^list/$', self.wrapper(self.changeList_view), name=self.get_list_url_name),
            re_path(r'^add/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            re_path(r'^change/(?P<pk>\d+)$', self.wrapper(self.change_view), name=self.get_change_url_name),
            re_path(r'^delete/(?P<pk>\d+)$', self.wrapper(self.delete_view), name=self.get_delete_url_name),
        ]
        patterns.extend(self.extra_urls())  # self 为那个 model.表名来调用则即为谁，
        return patterns

    def extra_urls(self):
        """
        用于超出四个 url 时增加 url，额外增加 url
        可在列表中增加除上面四个 urls 之外的 url 地址
        :return:
        """
        return []


class StarkSite():
    """
    自动生成 url 类
    """

    def __init__(self):
        self._registry = []
        self.app_name = 'stark'
        self.namespace = 'stark'

    def register(self, model_class, handler_class=None, prev=None):
        """

        :param model_class: 接收应用 app 中 models 中的数据库表的类(即在每个应用 model 中用来创建数据库表的类名)
        :param handler_class:  处理请求的视图函数所在的类(即每个应用中 stark 模块中定义类对 model 中对数据库操作相关的类)
        :param prev: 生成 Url 前缀
        :return:
        """
        if not handler_class:  # 判断，如果 handler_class 等于空则指定 handler 等于 StarkHandler 类
            handler_class = StarkHandler
        self._registry.append(
            {'model_class': model_class, 'handler': handler_class(self, model_class, prev), 'prev': prev})

    def get_urls(self):
        """
        获取 urls
        方法说明：
            model_class 为app应用中 stark 模块传过来的 model.类名，
            _meta.app_label 获取的为 model_class 类名称所在的 app 名称
            _meta.model)name 获取的为 model_class 类名(即创建表名类) 的小写名称
        :return:
        """
        patterns = []
        for item in self._registry:
            model_class = item['model_class']
            handler = item['handler']
            prev = item['prev']
            app_label, model_name = model_class._meta.app_label, model_class._meta.model_name
            # 自动生成 url 地址并添加到 patterns 列表中
            if prev:  # 判断如果 prev(前缀) 不为空则给生成的 url 地址添加前缀)
                patterns.append(
                    re_path(r'^%s/%s/%s/' % (app_label, model_name, prev,), (handler.get_urls(), None, None)))
            else:
                patterns.append(re_path(r'^%s/%s/' % (app_label, model_name), (handler.get_urls(), None, None)))
        return patterns

    @property
    def urls(self):
        """
        返回 urls 地址，selt.get_urls() 为 get_urls 函数中返回的列表，
        第二个为应用名称，第三个为 namespace
        :return:
        """
        return self.get_urls(), self.app_name, self.namespace


site = StarkSite()
