from django.conf.urls import url

from . import views

print 'HELLO WORLD FROM STANDARDDEVELOPER 1!'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url('NewStudy',views.NewStudy),
    url('QueryStudy',views.QueryStudy),
    url('NewSource',views.NewSource),
    url('QueryStandardDSMD',views.QueryStandardDSMD),
    url('NewDS',views.NewDS),
    url('SetMDVar',views.SetMDVar),
    url('NewVar',views.NewVar),
    url('test',views.Test1),
    url('GetAllGlobalCL',views.GetAllGlobalCL),
    url('Get1GlobalCodeList',views.Get1GlobalCodeList),
    url('NewMerge',views.NewMerge),
    url('NewModel',views.NewModel),
    url('GetStudySources',views.GetStudySources),
    url('QSDS',views.QueryStudyDS),
    url('GetStandards',views.GetStandards),
    url('GetStudies',views.GetStudies),
    url('EditStudyDS',views.ESDS),

    url('ModifyaDataset',views.modds),
    url('ModifyaVariable',views.modvar),
    url('ModifyVars',views.modvar),
    url('Predecessors',views.predlist),
    url('Merge',views.merge),
    url('Model',views.model)
]

