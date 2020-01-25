from django.contrib.admin import site,ModelAdmin,register
from datetime import datetime,timedelta,timezone

from .models import *
from crawl.admin import *

site.register(Source, BaseSourceAdmin)
site.register(CrawlRun, BaseCrawlRunAdmin)

class ItemDataInline(BaseItemDataInline):
    model = ItemData

class ItemLogInline(BaseItemLogInline):
    model = ItemLog

@register(Item)
class ItemAdmin(BaseItemAdmin):
    actions = ['make_inactive','make_active','delete_inactive']
    inlines = [
        ItemDataInline,
        ItemLogInline,
    ]

    def make_inactive(self, request, queryset):
        rows_updated=queryset.update(active=False)
        if rows_updated == 1:
            message_bit = "1 item was"
        else:
            message_bit = "%s items were" % rows_updated
        self.message_user(request, "%s successfully marked as inactive." % message_bit)
    make_inactive.short_description = "Mark selected items as inactive"

    def make_active(self, request, queryset):
        rows_updated=queryset.update(active=True)
        if rows_updated == 1:
            message_bit = "1 item was"
        else:
            message_bit = "%s items were" % rows_updated
        self.message_user(request, "%s successfully marked as active." % message_bit)
    make_active.short_description = "Mark selected items as active"

    def delete_inactive(self, request, queryset):
        objs = queryset.model.objects.filter(active=False,created_at__lt=datetime.now(timezone.utc)-timedelta(2)).delete()
        self.message_user(request, "%s items successfully deleted." % objs[0])
    delete_inactive.short_description="delete inactive items added 2 days ago"

@register(ItemLog)
class ItemLog(BaseItemLogAdmin):
    pass

