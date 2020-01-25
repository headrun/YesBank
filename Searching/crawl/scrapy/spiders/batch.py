from .base import *

class BatchPage(BasePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BatchSpider(BaseSpider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        objs = getattr(self.item_model, 'items', None)

    def start_requests(self):
        batchsize = self.custom_settings.get('BATCHSIZE',1)
        for i in range(0, len(self.keys), batchsize):
            yield self.create_main_batch_page(self.keys[i:i+batchsize])

    def create_main_batch_page(self, keys):
        item_log_dict = {}
        for key in keys:
            item_log_dict[key] = self.create_item_log(self.item_model, key)

        page = self.main_page_class(None, spider=self, keys=keys, item_log_dict=item_log_dict)
        try:
            return self.create_request(page)
        except Exception as e:
            self.save_error(page, str(e))
            raise e
        
    def get_batch_item(self, page, key, obj, save_item_log):
        kwargs = {'key': key, 'item_log': save_item_log}
        if isinstance(obj, BasePage):
            obj.set_kwargs(kwargs)
            return obj
        else:
            return DataPage(page, obj, **kwargs)
    
