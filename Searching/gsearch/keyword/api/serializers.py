from crawl.api.serializers import *

from ..models import *

class SourceSerializer(BaseSourceSerializer):
    class Meta(BaseSourceSerializer.Meta):
        model = Source

class ListCreateSerializer(BaseItemListCreateSerializer):
    source = SourceSerializer(default={'name': BaseSource.UNKNOWN})

    class Meta(BaseItemListCreateSerializer.Meta):
        model = Item

class DetailSerializer(BaseItemDetailSerializer):
    source = SourceSerializer()

    class Meta(BaseItemDetailSerializer.Meta):
        model = Item
