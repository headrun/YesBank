from django.conf.urls import url
from django.urls import reverse
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from oauth2_provider.contrib.rest_framework import IsAuthenticatedOrTokenHasScope

from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND,HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import CursorPagination
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.mixins import UpdateModelMixin

from base.settings import DjangoUtil;
settings = DjangoUtil.settings()

def url_prefix(version):
    return r'v%d/' % version

def model(obj):
    if hasattr(obj, 'model'):
        return obj.model
    elif hasattr(obj, 'serializer_class'):
        return obj.serializer_class.Meta.model

def app_label(obj):
    return model(obj)._meta.app_label

def url_name(obj, name):
    return app_label(obj) + '_' + model(obj)._meta.model_name + ('_' + name if name else name)

class APIPermission(IsAuthenticatedOrTokenHasScope):
    def has_permission(self, request, view):
        ret = super().has_permission(request, view)
        return request.user.is_staff if request.user and request.user.is_authenticated else ret

class CrawlCursorPagination(CursorPagination):
    ordering = 'updated_at'
    page_size_query_param = 'page_size'
    page_size = 10
    max_page_size = 100

class UrlMixin:
    permission_classes = [APIPermission] if not settings.DEBUG else []

    @classmethod
    def get_url(self, *args):
        return reverse(url_name(self, self.view_name), args=args)

    @classmethod
    def urlpatterns(self, version):
        name = url_name(self, self.view_name)
        prefix = url_prefix(version) + app_label(self) + self.url_path
        return [
            url(prefix, self.as_view(), name=name),
        ]

class KeyMixin:
    lookup_field = 'key'
    lookup_url_kwarg = 'key'

    def get_queryset(self):
        key = self.kwargs.get('key',[])
        objs = model(self).objects
        if key:
            objs = model(self).objects.filter(key=key[0]).first()
            if objs==None:
                objs = model(self).objects.filter(key=key).first()
        return objs

    def get_object(self):
        return self.get_queryset()

class SourceKeyMixin:
    lookup_field = 'key'
    lookup_url_kwarg = 'key'

    def get_queryset(self):
        source_name = self.kwargs.get('source_name', self.kwargs.get('source', {}).get('name', ''))
        objs = model(self).objects.select_related('source')
        if source_name:
            objs = objs.filter(source__name=source_name)
        return objs

class ListCreateUpdateView(UrlMixin, KeyMixin, UpdateModelMixin, ListCreateAPIView):
    required_scopes = ['write']
    pagination_class = CrawlCursorPagination

    url_path = '/$'
    view_name = 'listcreate'

    def post(self, request, *args, **kwargs):
        try:
            self.kwargs.update(request.data)
            return self.update(request, *args, **kwargs)
        except Http404:
            try:
                return self.create(request, *args, **kwargs)
            except model(self).source.field.related_model.DoesNotExist:
                return HttpResponseBadRequest()
        except model(self).MultipleObjectsReturned:
            return HttpResponseBadRequest()

class DetailView(UrlMixin, SourceKeyMixin, RetrieveAPIView):
    required_scopes = ['read']

    url_path = '/(?P<source_name>[-\.\w]+)/(?P<key>[-\.\w\s]+)/$'
    view_name = ''

    @classmethod
    def urlpatterns(self, version):
        return format_suffix_patterns(super().urlpatterns(version))

    def get_serializer(self, instance):
        serializer = super().get_serializer(instance)
        data = serializer.data['data']
        if not data or data.get('http_status', None):
            e = model(self).InvalidDataException()
            e.http_status = data.get('http_status', HTTP_204_NO_CONTENT)
            raise e
        return serializer

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except model(self).InvalidDataException as e:
            return Response(status=e.http_status)

class DetailListView(UrlMixin, SourceKeyMixin, ListAPIView):
    required_scopes = ['read']

    url_path = '/(?P<key>[-\.\w\s]+)/$'
    view_name = 'keylist'

    @classmethod
    def urlpatterns(self, version):
        return format_suffix_patterns(super().urlpatterns(version))

    def get_queryset(self):
        objs = super().get_queryset()
        return objs.select_related('source').prefetch_related('data_list').filter(key=self.kwargs['key'])

    def list(self, request, *args, **kwargs):
        if not self.get_queryset().exists():
            return Response(status=HTTP_404_NOT_FOUND)

        return super().list(request, *args, **kwargs)
