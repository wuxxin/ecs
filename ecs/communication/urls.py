from django.conf.urls import url

from ecs.communication import views


urlpatterns = (
    url(r'^list/$', views.list_threads),
    url(r'^widget/incoming/(?:(?P<submission_pk>\d+)/)?$', views.incoming_message_widget),
    url(r'^widget/outgoing/(?:(?P<submission_pk>\d+)/)?$', views.outgoing_message_widget),
    url(r'^widget/overview/(?P<submission_pk>\d+)$', views.communication_overview_widget),
    url(r'^new/(?:(?P<submission_pk>\d+)/)?(?:(?P<to_user_pk>\d+)/)?$', views.new_thread),
    url(r'^(?P<thread_pk>\d+)/read/$', views.read_thread),
    url(r'^(?P<thread_pk>\d+)/close/$', views.close_thread),
)
