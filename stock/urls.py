from django.conf.urls import url

from . import views

app_name = 'stock'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^kiwoom/$', views.kiwoom, name='kiwoom'),
]
