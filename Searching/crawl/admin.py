from django.db.models import Prefetch
from django.contrib.admin import register, ModelAdmin, TabularInline
from django.utils.html import format_html, format_html_join

from .models import Proxy, SourceGroup, BaseSource

@register(Proxy)
class ProxyAdmin(ModelAdmin):
    list_display = ('name', 'headers', 'servers')

@register(SourceGroup)
class SourceGroupAdmin(ModelAdmin):
    list_display = ('order', 'name', 'headers', 'settings')
    ordering = ('-order', )

    
class BaseSourceAdmin(ModelAdmin):
    list_display = ('name', 'active', 'deployed', 'proxy', 'headers', 'settings', 'group_names', 'url', 'fullname')
    list_filter = ('active', 'deployed', 'groups')
    filter_horizontal = ('groups',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('proxy').prefetch_related('groups')

    def group_names(self, obj):
        return ','.join([o.name for o in obj.groups.all()])

    def headers(self, obj):
        if not hasattr(obj, 'headers'):
            obj.set_group_values()
        return obj.headers

    def settings(self, obj):
        if not hasattr(obj, 'settings'):
            obj.set_group_values()
        return obj.settings

class BaseItemDataInline(TabularInline):
    fields = ('name', 'order', 'hashkey', 'json')
    readonly_fields = ('name', 'order', 'hashkey', 'json')

class BaseItemLogInline(TabularInline):
    fields = ('crawl_run', 'spider', 'status_str', 'message', 'created_at')
    readonly_fields = ('crawl_run', 'spider', 'status_str', 'message', 'created_at')

    def message(self, obj):
        try:
            return format_html(obj.msg.replace('\n', '<br />'))
        except:
            return obj.msg

class BaseItemAdmin(ModelAdmin):
    list_display = ('id', 'source', 'key', 'active', 'status')
    fields = (('source', 'key'), 'status', 'active')
    readonly_fields = ('source', 'key', 'status')
    search_fields = ('source__name', 'key')
    list_filter = ('active', 'source')
    list_per_page = 10

class BaseCrawlRunAdmin(ModelAdmin):
    list_display = ('id', 'source', 'msg', 'time_taken_in_sec', 'num_items', 'created_at', 'status_stats', 'brief_stats')
    fields = (('created_at', 'updated_at'), ('source', 'msg'), ('num_items', 'time_taken_in_sec'), 'source_stats', 'crawl_stats')
    readonly_fields = ('created_at', 'updated_at', 'source', 'msg', 'num_items', 'time_taken_in_sec', 'source_stats', 'crawl_stats')
    list_filter = ('source', )
    list_per_page = 10

    LOGS_NAMES = ('item_logs',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        for logs_name in self.LOGS_NAMES:
            qs = self.prefetch_logs(request, qs, logs_name)
        return qs

    def prefetch_logs(self, request, qs, logs_name):
        log_model = getattr(self.model, logs_name).field.model
        qs = qs.prefetch_related(
                Prefetch(logs_name,
                    queryset=log_model.objects.only('crawl_run', 'status', 'item'),
                )
            )
        if request.resolver_match.func.__name__ == 'change_view':
            item_model = log_model.item.field.related_model
            self.source_model = item_model.source.field.related_model
            qs = qs.prefetch_related(
                    Prefetch(logs_name + '__item',
                        queryset=item_model.objects.only('source'),
                    ),
                    Prefetch(logs_name + '__item__source',
                        queryset=self.source_model.objects.only('name'),
                    )
                )
        return qs

    def dict_to_html(self, dt):
        return format_html_join('\n', "<li><b>{}:</b> {}</li>", ((key, val) for key, val in dt.items()))

    def brief_stats(self, obj):
        keys = ('start_time', 'finish_time', 'finish_reason', 'elapsed_time_seconds',
                'downloader/request_count', 'downloader/response_count', 'downloader/response_status_count')
        return self.dict_to_html({x: y for x, y in obj.stats.items() for key in keys if x.startswith(key)})

    def crawl_stats(self, obj):
        return self.dict_to_html(obj.stats)

    def num_items(self, obj):
        return obj.item_logs.count()

    def status_stats(self, obj):
        dt = {}
        for log in self.get_logs(obj):
            status = log.status_str()
            if status in dt:
                dt[status] += 1
            else:
                dt[status] = 1
        return self.dict_to_html(dt)

    def source_stats(self, obj):
        if obj.source.name != BaseSource.UNKNOWN:
            return self.status_stats(obj)

        name_list = self.source_model.active_objects.values_list('name', flat=True)
        dt = {'SPIDERS': len(name_list)}
        dt.update({name: {} for name in name_list})
        for log in self.get_logs(obj):
            val = dt.setdefault(log.item.source.name, {})
            status = log.status_str()
            if status in val:
                val[status] += 1
            else:
                val[status] = 1
        return self.dict_to_html(dt)

    def get_logs(self, obj):
        logs = []
        for logs_name in self.LOGS_NAMES:
            logs += list(getattr(obj, logs_name).all())
        return logs

class BaseItemLogAdmin(ModelAdmin):
    list_display = ('id', 'crawl_run', 'item', 'spider', 'status_str', 'message', 'time_taken_in_sec', 'created_at')
    fields = (('crawl_run', 'item', 'spider'), ('status_str', 'msg'), ('created_at', 'updated_at'))
    readonly_fields = ('crawl_run', 'item', 'spider', 'status_str', 'msg', 'created_at', 'updated_at')
    search_fields = ('item__source__name', 'item__key')
    list_filter = ('status', 'item__source')
    list_per_page = 10

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).prefetch_related('crawl_run')

    def message(self, obj):
        try:
            return format_html(obj.msg.replace('\n', '<br />'))
        except:
            return obj.msg

