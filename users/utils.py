# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils.functional import wraps

from ecs.users.middleware import current_user_store

def get_current_user():
    if hasattr(current_user_store, 'user'):
        return current_user_store.user
    else:
        return None
        # FIXME: what do we return during testing or management commands? Do we really query the user table every time?
        #return User.objects.get(username='root')
        
class sudo(object):
    def __init__(self, user=None):
        self.user = user

    def __enter__(self):
        from ecs.users.middleware import current_user_store
        self._previous_user = getattr(current_user_store, 'user', None)
        user = self.user
        if callable(user):
            user = user()
        current_user_store.user = user
        
    def __exit__(self, *exc):
        from ecs.users.middleware import current_user_store
        current_user_store.user = self._previous_user
        
    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return decorated
        