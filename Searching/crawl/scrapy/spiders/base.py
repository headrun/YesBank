import random

from django.utils import timezone

from scrapy import Spider

from base.utils import import_module_var

from ..validators import *

class BasePage:
    def __init__(self, parent_page, **kwargs):
        self.parent_page = parent_page

        self.kwargs = {}
        if parent_page:
            self.set_kwargs(parent_page.kwargs)
        self.set_kwargs(kwargs)

    def request(self):
        return

    def errback(self, response):
        return

    def parse(self, response):
        return OKSchemaItem()

    def set_kwargs(self, kwargs):
        self.kwargs.update(kwargs)
        self.__dict__.update(kwargs)

class DataPage(BasePage):
    def __init__(self, parent_page, obj, **kwargs):
        self.obj = obj
        super().__init__(parent_page, **kwargs)

    def request(self):
        return self.spider.get_data(self, self.obj)

class BaseSpider(Spider):
    main_page_class = None

    @classmethod
    def get_source_name(cls):
        return cls.source_name if hasattr(cls, 'source_name') else cls.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.crawl_run = kwargs.get('crawl_run', None)

        self.item_model = kwargs.get('item_model', None)
        if isinstance(self.item_model, str):
            self.item_model = import_module_var(self.item_model, None)
        self.source_model   = self.item_model.source.field.related_model

        self.source = self.source_model.objects.select_related('proxy').prefetch_related('groups').get(name=self.get_source_name())
        self.source.set_group_values()

        self.keys = kwargs.get('keys', None)
        if not self.keys:
            raise Exception('Invalid Keys')
        if isinstance(self.keys, str):
            if self.keys[0] == '[':
                self.keys = eval(self.keys)
            else:
                self.keys = [x for x in self.keys.split(',') if x]
        self.keys_set = set(self.keys)

    def start_requests(self):
        return self.create_main_pages()

    def create_main_pages(self):
        for key in self.keys:
            yield self.create_main_page(key)

    def create_main_page(self, key):
        item_log = self.create_item_log(self.item_model, key)

        page = self.main_page_class(None, spider=self, key=key, item_log=item_log)

        try:
            return self.create_request(page)
        except Exception as e:
            self.save_error(page, str(e))
            raise e

    def errback(self, response):
        page = response.request.meta['page']
        obj = page.errback(response)
        if obj:
            return self.get_data(page, obj)

        msg = str(response.value.response.status if hasattr(response.value, 'response') else str(response.value))
        self.save_error(page, msg)

    def parse(self, response):
        page = response.meta['page']
        try:
            obj = page.parse(response)
            objs = obj if isinstance(obj, list) else [obj]
            for obj in objs:
                if isinstance(obj, BasePage):
                    yield self.create_request(obj)
                elif isinstance(obj, BaseSchemaItem) or \
                        isinstance(obj, dict):
                    for o in self.handle_groups(obj):
                        yield o
                    yield self.get_data(page, obj)
                else:
                    for o in self.handle_data(page, obj):
                        yield o
        except Exception as e:
            self.save_error(page, str(e))
            raise e

    def create_request(self, page):
        req = page.request()
        if isinstance(req, dict):
            return req

        if req:
            req.meta['page'] = page
            req.headers.update(self.source.headers)
            self.init_proxy(req, self.source.proxy)

            req.callback = self.parse
            req.errback = self.errback
            return req

    def get_data(self, page, obj):
        data = {'source': self.get_source_name(), 'data': obj}
        data.update(page.kwargs)
        return data

    def handle_data(self, page, obj):
        raise Exception('BasePage.parse must return BasePage, BaseSchemaItem or dict. page %s returned %s' % (page, obj))

    def handle_groups(self, obj):
        groups = obj.get('groups', [])
        for group in groups:
            for key in set(group.keys).difference(self.keys_set):
                self.keys_set.add(key)
                yield self.create_main_page(key)

    def create_item_log(self, item_model, key):
        item, flag = item_model.objects.get_or_create(source=self.source, key=key)
        item.source = self.source

        itemlog_model  = item_model.logs.field.model
        return itemlog_model.objects.create(crawl_run=self.crawl_run, item=item, spider=self.name)

    def init_proxy(self, req, proxy):
        if not proxy:
            return
        req.meta['proxy'] = random.choice(proxy.servers)
        if proxy.headers:
            for name, value in proxy.headers.items():
                req.headers[name] = value

    def save_error(self, page, msg):
        msg = page.__class__.__name__ + ':' + msg

        if not hasattr(page, 'item_log'):
            return
        item_log = page.item_log
        item_log.status = item_log.STATUS_FAILURE
        item_log.msg    = item_log.msg + ('\n' if item_log.msg else '') + msg
        item_log.save()

