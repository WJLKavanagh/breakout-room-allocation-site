from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:participants>over<int:rounds>', views.query, name='query'),
]