from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import login
from django.views.static import serve
from ecs.utils import forceauth
import django

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/dashboard/'}),

    url(r'^core/', include('core.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^docstash/', include('docstash.urls')),
    url(r'^accounts/login/$', forceauth.exempt(login), {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^feedback/', include('ecs.feedback.urls')),
    url(r'^userswitcher/', include('ecs.userswitcher.urls')),
    url(r'^pdfviewer/', include('ecs.pdfviewer.urls')),
    url(r'^mediaserver/', include('ecs.mediaserver.urls')),
    url(r'^tasks/', include('ecs.tasks.urls')),
    url(r'^messages/', include('ecs.messages.urls')),

    url(r'^static/(?P<path>.*)$', forceauth.exempt(serve), {'document_root': settings.MEDIA_ROOT}),
    url(r'^trigger500/$', lambda request: 1/0),

    #url(r'^tests/killableprocess/$', 'ecs.utils.tests.killableprocess.timeout_view'),
)

