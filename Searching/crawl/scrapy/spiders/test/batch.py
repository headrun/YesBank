from scrapy.http import Request

from ..batch import *

class MainPage(BatchPage):
    def request(self):
        return Request('http://localhost:8000/static/admin/css/fonts.css?main=%s' % (','.join(self.keys)))

    def parse(self, response):
        meta_items = []
        for key in self.keys:
            save_item_log = self.item_log_dict.get(key)
            if not save_item_log:continue
            meta_items.append(self.spider.get_batch_item(self, key, OKSchemaItem(), save_item_log))
        return meta_items
 
class TestSpider(BatchSpider):
    name = 'batch'
    source_name = 'test'
    custom_settings  = {'BATCHSIZE': 2}
    main_page_class = MainPage
