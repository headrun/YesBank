from .login import *

class UserLoginPage(LoginPage):
    def __init__(self, *args, **kwargs):
        self.crawl_user = kwargs['item_log'].item
        super().__init__(*args, **kwargs)

class UserSpider(BaseSpider):
    MODEL = 'CrawlUser'
    custom_settings = {'COOKIES_ENABLED': True}    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        objs = getattr(self.item_model, 'items', None)
        if not objs:
            raise Exception('Incompatible spider used for model %s' % self.item_model)

        self.save_item_model = objs.field.related_model

    def get_user_item(self, page, key, obj):
        save_item_log = self.create_item_log(self.save_item_model, key)
        page.item_log.item.items.add(save_item_log.item)

        kwargs = {'key': key, 'item_log': save_item_log}
        if isinstance(obj, BasePage):
            obj.set_kwargs(kwargs)
            return obj
        else:
            return DataPage(page, obj, **kwargs)
