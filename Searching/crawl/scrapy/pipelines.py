# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import traceback

from django.core.exceptions import FieldDoesNotExist

from .validators import *

class DjangoPipeline(object):
    def process_item(self, data, spider):
        item_log, item_data = data['item_log'], data['data']
        item = item_log.item

        try:
            self.save_item_data(item, item_data)

            spider.logger.info('Spider: %s, item: %s' % (spider.name, item))
            if getattr(spider, 'unknown', None):
                spider.item_model.objects.filter(source__name=spider.source_model.UNKNOWN, key=data['key'], active=True).update(active=False)
                spider.logger.info('unknown')

            self.update_item(item, data)

            item_log.status = item_log.STATUS_SUCCESS
        except Exception as e:
            traceback.print_exc()
            item_log.status = item_log.STATUS_FAILURE
            item_log.msg    = self.__class__.__name__ + ':' + str(e)
        item_log.save()

    def update_item(self, item, data):
        val = data['data']
        if 'active' in data:
            item.active = data['active']
        if isinstance(val, InvalidSchemaItem):
            item.active = False
            item.status = val.http_status
        item.save()

    def save_item_data(self, item, item_data):
        if not hasattr(item, 'data_list'):
            return

        hashkey_exists = False
        try:
            item.data_list.field.model._meta.get_field('hashkey')
            hashkey_exists = True
        except FieldDoesNotExist:
            pass

        kwargs = {x: item_data.get(x, None) for x in ('name', 'order')}
        hashkey = item_data.get('hashkey', None)
        groups = item_data.get('groups', [])
        if isinstance(item_data, EmptyDataSchema):
            return
        if isinstance(item_data, BaseSchemaItem):
            item_data.validate()
            item_data = item_data.serialize()

        if 'groups' in item_data and not groups:
            del item_data['groups']
        self.save_item_groups(item, groups)

        obj = None
        for k in [None] + ([hashkey] if hashkey and hashkey_exists else []):
            if hashkey_exists:
                kwargs['hashkey'] = k
            try:
                obj = item.data_list.get(**kwargs)
            except item.data_list.field.model.DoesNotExist:
                continue
            break

        if obj:
            obj.json = item_data
            if hashkey_exists:
                obj.hashkey = hashkey
            obj.save()
        else:
            kwargs['json'] = item_data
            if hashkey_exists:
                kwargs['hashkey'] = hashkey
            item.data_list.create(**kwargs)

    def save_item_groups(self, item, groups):
        if not hasattr(item, 'groups'):
            return

        for group in groups:
            keys = [item.key] + group.keys
            items = item.__class__.objects.filter(source=item.source, key__in=keys)

            group_model = item.groups.target_field.related_model
            obj, flag = group_model.objects.get_or_create(name=group.name, key=group.key(item.key))
            obj.items.add(*items)
