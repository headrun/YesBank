from crawl.models import *

class Source(BaseSource):
    class Meta(BaseSource.Meta):
        pass

class CrawlRun(BaseCrawlRun):
    source  = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='crawl_runs')

    class Meta(BaseCrawlRun.Meta):
        pass

class ItemGroup(BaseItemGroup):

    class Meta(BaseItemGroup.Meta):
        pass

class Item(BaseItem):
    source          = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='items')

    groups          = models.ManyToManyField(
                        ItemGroup,
                        blank=True,
                        related_name='items',
                    )

    class Meta(BaseItem.Meta):
        unique_together = (('source', 'key'), )

class ItemData(BaseData):
    item        = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='data_list')

    class Meta(BaseData.Meta):
        unique_together = (('item', 'name', 'order'), )
        indexes = [
            models.Index(fields=('item', 'name', 'order')),
        ]

class ItemLog(BaseLog):
    crawl_run   = models.ForeignKey(CrawlRun, null=True, blank=True, on_delete=models.CASCADE, related_name='item_logs')
    item        = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='logs')

    class Meta(BaseLog.Meta):
        pass
