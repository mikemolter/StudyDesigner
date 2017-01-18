from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url('DBCodelists',views.dbcodelists),
    url('Child',views.ChildrenCL),
    url('Back2DBCodeList',views.Back2DBCodeList),
]