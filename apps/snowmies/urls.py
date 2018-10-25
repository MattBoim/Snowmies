from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index),
    url(r'^process$', views.process),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
    url(r'^selectresort$', views.selectresort),
    url(r'^processresort$', views.processresort),
    url(r'^dashboard$', views.dashboard),
    url(r'^addRide$', views.addRide),
    url(r'^processadd$', views.processadd),
    url(r'^destroy_data$', views.destroy_data),
    url(r'^edit/(?P<id>\d+)$', views.edit),
    url(r'^processedit/(?P<id>\d+)$', views.processedit),
    url(r'^remove/(?P<id>\d+)$', views.remove),
]