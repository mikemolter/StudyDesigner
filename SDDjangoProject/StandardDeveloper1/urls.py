from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url('DFNew',views.dfnew),
    url('ModifyaDataset',views.modds),
    url('ModifyVars',views.modvar),
    url('Predecessors',views.predlist)
]

