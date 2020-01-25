from crawl.scrapy.pipelines import DjangoPipeline as BasePipeline
from .validators import *

class DjangoPipeline(BasePipeline):
    def process_item(self, data, spider):
        val = data['data']
        if isinstance(val,TrackingMeta):
            data['item_log'].item.active=False
            data['item_log'].item.status=200
            data['data']=TrackingMeta(val)
        super().process_item(data, spider)
