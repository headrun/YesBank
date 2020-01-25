from crawl.api import views as api

from .serializers import *

class ListCreateUpdateView(api.ListCreateUpdateView):
    serializer_class = ListCreateSerializer

class DetailView(api.DetailView):
    serializer_class = DetailSerializer

class DetailListView(api.DetailListView):
    serializer_class = DetailSerializer
