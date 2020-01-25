from .views import *

version=1

views = [
    DetailView,
    DetailListView,
    ListCreateUpdateView,
]

urlpatterns = []
[urlpatterns.extend(view.urlpatterns(version)) for view in views]
