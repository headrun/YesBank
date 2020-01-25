from base.settings.scrapy import *

ITEM_PIPELINES = {
    'crawl.scrapy.pipelines.DjangoPipeline': 300,
}
