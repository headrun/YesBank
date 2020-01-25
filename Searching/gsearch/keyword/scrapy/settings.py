from base.settings.scrapy import *

ITEM_PIPELINES = {
    'gsearch.keyword.scrapy.pipelines.DjangoPipeline': 300,
}
