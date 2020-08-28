from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:participants>over<int:rounds>', views.query, name='query'),
    path('download/<int:alloc_id>', views.download, name="to_download"),
    path('parse/<int:alloc_id>', views.parse, name="parse"),
    path('parse/<int:alloc_id>/match_upload', views.parse_upload, name="parse_upload"),
    path('parse/<int:alloc_id>/match_text', views.parse_text, name="parse_text")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)