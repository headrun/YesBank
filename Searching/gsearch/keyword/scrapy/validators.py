import re

from schematics.models import Model
from schematics.types.compound import ListType, ModelType
from schematics.exceptions import ValidationError

from crawl.scrapy.validators import *

class MetaData(Model):
    url = StringType(required=True)
    title = StringType(required=True)
    description = StringType(required=True)

class TrackingMeta(BaseSchemaItem):
    searchData = ListType(ModelType(MetaData), required=True)
    rightSideData = DictType(StringType)
