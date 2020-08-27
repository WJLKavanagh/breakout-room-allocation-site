from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:participants>over<int:rounds>', views.query, name='query'),
    path('download/<int:alloc_id>', views.download, name="to_download"),
    path('parse/<int:alloc_id>', views.parse, name="to_parse")
]