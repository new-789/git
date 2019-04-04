from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class StarkConfig(AppConfig):
    name = 'stark'

    def ready(self):
        """
        定义此方法后表示会每次先加载 url 前执行每个应用中的
        stark 模块中的内容
        :return:
        """
        autodiscover_modules('stark')