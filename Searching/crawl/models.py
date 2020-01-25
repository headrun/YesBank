from django.db import models
from django.utils.functional import cached_property

from django_mysql.models import JSONField, ListTextField

from base.models import *

from .field import *

class Proxy(BaseModel):
    name            = models.CharField(
                        max_length=MAX_LENGTH_NAME,
                        unique=True
                    )
    headers         = JSONField(
                        null=True, blank=True,
                        help_text='{<br/>"Proxy-Authorization": "Basic xxxxxx",<br/> ...<br/>}'
                    )
    servers         = ListTextField(
                        base_field=models.CharField(max_length=MAX_LENGTH_LONG_NAME),
                        help_text='comma-separated urls.<br/>https://www.example.com:6060, ...<br/>'
                    )

    class Meta(BaseModel.Meta):
        pass

    def __str__(self):
        return '%s' % self.name

class SourceGroup(BaseGroupModel):
    headers         = JSONField(
                        null=True, blank=True,
                        help_text='{<br/>"key": "value",<br/> ...<br/>}'
                    )
    settings        = JSONField(
                        null=True, blank=True,
                        help_text='{<br/>"ROBOTSTXT_OBEY": false,<br/> ...<br/>}'
                    )

    class Meta(BaseGroupModel.Meta):
        unique_together = (('name', ), ('order', ))

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)

class SourceActiveManager(ActiveManager):
    def get_queryset(self):
        return super().get_queryset().exclude(name=BaseSource.UNKNOWN)

class BaseSource(TimeModel):
    UNKNOWN         = '--'

    name            = models.CharField(max_length=MAX_LENGTH_NAME)
    fullname        = models.CharField(max_length=MAX_LENGTH_MSG)
    url             = models.CharField(max_length=MAX_LENGTH_LONG_NAME)

    active          = models.BooleanField(default=True)
    deployed        = models.BooleanField(default=True)

    proxy           = models.ForeignKey(Proxy, null=True, blank=True, on_delete=models.CASCADE, related_name='+')
    groups          = models.ManyToManyField(
                        SourceGroup,
                        blank=True,
                        related_name="%(app_label)s_%(class)ss",
                        related_query_name="%(app_label)s_%(class)ss"
                    )

    objects         = models.Manager()
    active_objects  = SourceActiveManager()

    class Meta(TimeModel.Meta):
        abstract = True
        unique_together = (('name', 'url'), )
        ordering = ('name',)

    def __str__(self):
        return self.name

    def set_group_values(self):
        self.headers, self.settings = {}, {}
        for group in self.groups.all():
            self.headers.update(group.headers)
            self.settings.update(group.settings)

class ItemActiveManager(ActiveManager):
    def get_queryset(self):
        return super().get_queryset().select_related('source').filter(source__active=True)

class BaseItemGroup(BaseGroupModel):
    key             = models.CharField(max_length=MAX_LENGTH_ID)

    class Meta(BaseGroupModel.Meta):
        abstract = True
        unique_together = (('name', 'key'), )

class BaseItem(TimeModel):
    key             = models.CharField(max_length=MAX_LENGTH_ID)

    active          = models.BooleanField(default=True)
    status          = TruncatingCharField(max_length=MAX_LENGTH_MSG, null=True, blank=True)

    # Managers
    objects         = models.Manager()
    active_objects  = ItemActiveManager()

    class Meta(TimeModel.Meta):
        abstract = True

    class InvalidDataException(Exception):
        """ data_list does not have valid data. """

    def __str__(self):
        return '%s/%s' % (getattr(self, 'source', BaseSource.UNKNOWN), self.key)

class BaseData(TimeModel):
    #item           = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='data_list')

    name            = models.CharField(max_length=MAX_LENGTH_NAME, null=True, blank=True)
    order           = models.PositiveSmallIntegerField(null=True, blank=True)

    json            = JSONField()

    hashkey         = models.CharField(max_length=MAX_LENGTH_ID, null=True, blank=True)

    class Meta(TimeModel.Meta):
        abstract = True
        ordering = ('name', 'order', 'updated_at')

class BaseCrawlRun(BaseLogModel):
    #source          = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='crawl_runs')
    msg             = models.CharField(max_length=MAX_LENGTH_MSG)

    stats           = JSONField()

    class Meta(BaseLogModel.Meta):
        abstract = True
        ordering = ('-updated_at', '-id')

class BaseLog(BaseLogModel):
    #crawl_run       = models.ForeignKey(CrawlRun, null=True, blank=True, on_delete=models.CASCADE, related_name='logs')

    STATUS_LIST = ['Pending', 'Success', 'Failure']
    STATUS_PENDING, STATUS_SUCCESS, STATUS_FAILURE = range(len(STATUS_LIST))
    status          = models.CharField(max_length=MAX_LENGTH_SHORT_NAME, default=STATUS_PENDING, choices=[(i, x) for i, x in enumerate(STATUS_LIST)])

    msg             = models.CharField(max_length=MAX_LENGTH_MSG)

    spider          = models.CharField(max_length=MAX_LENGTH_NAME)

    #item            = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='logs')
    #parent_log      = models.ForeignKey('Log', on_delete=models.CASCADE, related_name='child_logs', null=True, blank=True)

    class Meta(BaseModel.Meta):
        abstract = True

    def __str__(self):
        return '%s/%s' % (getattr(self, 'item', ''), self.created_at)

    def status_str(self):
        return self.STATUS_LIST[int(self.status)]

