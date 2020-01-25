from base.serializers import *

class BaseSourceSerializer(BaseModelSerializer):

    class Meta(BaseModelSerializer.Meta):
        fields = ['name', 'url', 'fullname']
        read_only_fields = ['url', 'fullname']

class BaseItemDetailSerializer(BaseModelSerializer):
    data = serializers.SerializerMethodField()

    class Meta(BaseModelSerializer.Meta):
        fields = ['source', 'key', 'active', 'data']

    def get_data(self, obj):
        data = {}
        for d in obj.data_list.all():
            if d.name is None:
                data.update(d.json)
            else:
                data.setdefault(d.name, []).append(d.json)

        return data

class BaseItemListCreateSerializer(BaseItemDetailSerializer):
    active = serializers.BooleanField(default=True)

    def create(self, validated_data):
        self.modify_input(validated_data)
        return super().create(validated_data)

    def update(self, obj, validated_data):
        self.modify_input(validated_data)
        return super().update(obj, validated_data)

    def modify_input(self, validated_data):
        source_model = self.fields['source'].Meta.model
        source_name = validated_data.pop('source').get('name', '')
        if not source_name:
            raise source_model.DoesNotExist

        validated_data['source'] = source_model.objects.get(name=source_name)
