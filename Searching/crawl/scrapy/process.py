import os, sys, logging, traceback
from optparse import OptionParser
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

sys.path.insert(1, os.getcwd())
from django.db.models import Max

from base.utils import standalone_main, init_logger, close_logger, import_module_var

class ItemProcess(CrawlerProcess):
    def parse(self):
        parser = OptionParser()
        parser.add_option("-d", "--debug", dest="debug", help="Debug logs", default=False, action='store_true')
        parser.add_option("-a", "--app-models", dest="app_models", default='', help="app models path. default is ${SCRAPY_PROJECT}.models.")
        parser.add_option("-s", "--spiders", dest="spiders", default='', help="',' separated spider names.")
        parser.add_option("-x", "--max-keys", dest="max_keys", type=int, default=-1, help="',' Maximum no. of keys per Source to be crawled.")

        (self.options, args) = parser.parse_args()

        models = self.options.app_models if self.options.app_models else '%s.models' % os.environ['SCRAPY_PROJECT']
        self.app_models = import_module_var(models, None)
        if not self.app_models:
            raise Exception('Unable to import module: %s' % models)

        self.spider_names = set([name for name in self.options.spiders.split(',') if name])

        self.log = init_logger(
            os.path.join(__file__.rstrip('.py') + '.log'),
            level=logging.DEBUG if self.options.debug else logging.INFO,
        )

    def process(self):
        spiders = [self.spider_loader.load(name) for name in self.spider_loader.list() if not self.spider_names or name in self.spider_names]
        self.log.info('App Models:%s' % self.app_models)
        self.log.info('spiders: %s' % spiders)

        item_model_dict = {}
        for spider in spiders:
            model_name = getattr(spider, 'MODEL', 'Item')
            item_model = item_model_dict.get(model_name, None)
            if not item_model:
                item_model_dict[model_name] = item_model = getattr(self.app_models, model_name, None)
                if not item_model:
                    raise Exception('%s does not have %s model' % (self.app_models, model_name))

        for spider in spiders:
            model_name = getattr(spider, 'MODEL', 'Item')
            item_model = item_model_dict.get(model_name, None)
            self.crawl_source(item_model, spider, self.get_source_name(spider))

        try:
            self.start()
        except:
            traceback.print_exc()
            return 1

    def close(self):
        close_logger(self.log)

    def crawl_source(self, item_model, spider, source_name):
        from crawl.models import BaseSource

        source_model    = item_model.source.field.related_model
        crawl_run_model = item_model.logs.field.model.crawl_run.field.related_model
        try:
            source = source_model.active_objects.prefetch_related('groups').get(name=source_name)
        except source_model.DoesNotExist:
            self.log.info('Skipping spider %s: source %s is not active.' % (spider.name, source_name))
            return

        source.set_group_values()
        spider.custom_settings = spider.custom_settings or {}
        spider.custom_settings.update(source.settings)

        crawl_run = crawl_run_model.objects.create(source=source)

        crawler = self.create_crawler(spider)

        unknown_keys = self.get_keys(BaseSource.UNKNOWN, item_model)
        self.log.info('Unknown keys = %s' % unknown_keys)
        if unknown_keys:
            self._crawl(crawler, crawl_run=crawl_run, item_model=item_model, keys=unknown_keys, unknown=True)

        keys = self.get_keys(source.name, item_model)
        self.log.info('spider = %s, source = %s, No. of keys = %s' % (spider.name, source_name, len(keys)))
        if keys:
            crawl_run.stats = crawler.stats._stats
            d = self._crawl(crawler, crawl_run=crawl_run, item_model=item_model, keys=keys)

            d.addBoth(self.stats_callback, crawl_run=crawl_run)
            d.addCallback(self.callback, crawl_run, spider)
            d.addErrback(self.errback, crawl_run, spider)

    def stats_callback(self, result, crawl_run):
        for key, val in crawl_run.stats.items():
            if isinstance(val, datetime):
                crawl_run.stats[key] = str(val)
        return result

    def callback(self, result, crawl_run, spider):
        crawl_run.save()

        self.log.info('Finished crawl_run = %s, spider = %s' % (crawl_run, spider))
        return result

    def errback(self, failure, crawl_run, spider):
        self.log.info('Error crawl_run = %s, spider = %s: %s' % (crawl_run, spider, failure.getTraceback()))

        crawl_run.msg = failure.value
        crawl_run.save()

        return failure

    def get_source_name(self, spider):
        return spider.get_source_name() if hasattr(spider, 'get_source_name') else spider.name

    def get_keys(self, source_name, item_model):
        objs = item_model.active_objects.filter(source__name=source_name) \
                .annotate(crawled_at=Max('logs__updated_at')).order_by('crawled_at', 'updated_at')
        if self.options.max_keys > 0:
            objs = objs[:self.options.max_keys]
        return list(objs.values_list('key', flat=True))

if __name__ == '__main__':
    standalone_main(ItemProcess, settings=get_project_settings())
