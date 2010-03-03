from django.conf.urls.defaults import *

import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    # Example:
    # (r'^ecs/', include('ecs.foo.urls')),
    url(r'^$', 'ecs.core.views.index'),

    url(r'^notification/new/$', 'ecs.core.views.select_notification_creation_type'),
    url(r'^notification/new/(?P<notification_type_pk>\d+)/$', 'ecs.core.views.create_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/$', 'ecs.core.views.view_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/upload-document/$', 'ecs.core.views.upload_document_for_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/pdf/$', 'ecs.core.views.notification_pdf'),
    url(r'^notifications/$', 'ecs.core.views.notification_list'),

    url(r'^document/(?P<document_pk>\d)/download/$', 'ecs.core.views.download_document'),

    url(r'^submission/(?P<submissionid>\d+)/$', 'core.views.submissiondetail'),
    url(r'^submission/', 'ecs.core.views.submission'),
)
