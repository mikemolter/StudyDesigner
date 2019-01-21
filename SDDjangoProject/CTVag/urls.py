from django.conf.urls import url

from . import views

print("HELLO WORLD!")

urlpatterns = [
    url(r'^$', views.index, name='idx'),
    url('DBChangeFromChild',views.DBChangeFromChild),
    url('DBChangeFromNew',views.DBChangeFromNew),
    url('DBCodelists',views.dbcodelists),
    url('Child',views.ChildrenCL),
    url('NewCh',views.NewChild),
    url('displayNCI',views.displayNCI),
    url('DBChangeFromAddNCI',views.DBChangeFromAddNCI),
    url('displayStudy',views.displayStudy),
    url('FromStudy',views.FromStudy)
]

print('URLPATTERNS: ') 
print(urlpatterns)
