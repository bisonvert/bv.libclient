"""Facilities for django 

"""
from django.conf import settings
import inspect

from libclient import LibUsers

def get_defaults_args(func):
    """Return the default arguments dict of a callable
    
    """
    args, varargs, varkwargs, defaults = inspect.getargspec(func)
    if not defaults:
        return {}
    index = len(args) - len(defaults)
    return dict(zip(args[index:], defaults))

def get_lib(lib, request):
    """Return a lib initialized with oauth_token and oauth_token_secret
    
    """
    kwargs = {
        'server_url': getattr(settings, 'OAUTH_SERVER_URL', None),
        'consumer_key': getattr(settings, 'OAUTH_CONSUMER_TOKEN'),
        'consumer_secret': getattr(settings, 'OAUTH_CONSUMER_SECRET'),
    }
    if request.session.get('oauth_token', False) and request.session.get('oauth_token_secret', False):       
        kwargs['token_key'] = request.session['oauth_token']
        kwargs['token_secret'] = request.session['oauth_token_secret']
    return lib(**kwargs)
    
def inject_lib(lib):
    """If lib is specified, inject the lib as last function argument.
    
    Use this decorator with django views like this::
    
        @inject_lib(lib=LibClass)
        def myview(request, lib):
            # make smthing with the lib here
    """
    def wrapper(func):
        def wrapped(*args, **kwargs):
            inspect.getargspec(func)
            if lib:
                request = args[0]
                if 'lib' in get_defaults_args(func):
                    kwargs['lib'] = get_lib(lib, request)
                else:
                    args = [arg for arg in args]
                    args.append(get_lib(lib, request))
            return func(*args, **kwargs)
        return wrapped
    return wrapper


class LazyUser(object):
    def __get__(self, request):
        if not hasattr(request, '_cached_user'):
            lib = getlib(LibUsers, request)
            request._cached_user = lib.get_active_user()
        return request._cached_user

class AuthenticationMiddleware(object):
    def process_request(self, request):
        """If some information is available in session about oauth token, 
        try to use it to authenticate to the BisonVert API, and provides a user
        in the request.

        """
        if 'oauth_token' and 'oauth_token_secret' in request.session:
            lib = get_lib(LibUsers, request)
            request.__class__.user = LazyUser()
        return None

class AuthenticationTemplateProcessor(object):
    pass
