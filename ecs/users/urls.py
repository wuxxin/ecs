from django.conf.urls import *

urlpatterns = patterns('ecs.users.views',
    url(r'^accounts/login/$', 'login'),
    url(r'^accounts/logout/$', 'logout'),
    url(r'^accounts/register/$', 'register'),

    url(r'^activate/(?P<token>.+)$', 'activate'),
    url(r'^profile/$', 'profile'),
    url(r'^profile/edit/$', 'edit_profile'),
    url(r'^profile/change-password/$', 'change_password'),
    url(r'^request-password-reset/$', 'request_password_reset'),
    url(r'^password-reset/(?P<token>.+)$', 'do_password_reset'),
    url(r'^users/(?P<user_pk>\d+)/indisposition/$', 'indisposition'),
    url(r'^users/notify_return/$', 'notify_return'),
    url(r'^users/(?P<user_pk>\d+)/toggle_active/$', 'toggle_active'),
    url(r'^users/(?P<user_pk>\d+)/details/', 'details'),
    url(r'^users/administration/$', 'administration'),
    url(r'^users/invite/$', 'invite'),
    url(r'^users/login_history/$', 'login_history'),
    url(r'^accept_invitation/(?P<invitation_uuid>[\da-zA-Z]{32})/$', 'accept_invitation'),
)
