"""Facilities to use the bv.libclient with django

Steps to follow to set up a django application:

    * add BVCLIENT_OAUTH_APPID="bisonvert" in you settings.py (matching the token
    identifier defined by the djangooauthclient app.
    * use the decorators when needed in you django views, eg::
        
        @inject_lib(LibCarpool)
        def my_view(request, param1, lib)

"""
from django.conf import settings
import inspect
from oauthclient.utils import get_consumer_token, is_oauth_authenticated, \
    need_oauth_authentication

from bv.libclient.libusers import LibUsers

oauth_identifier = getattr(settings, 'BVCLIENT_OAUTH_APPID', 'bisonvert')

def is_bvoauth_authenticated(request):
    return is_oauth_authenticated(request, oauth_identifier)

def need_bvoauth_authentication(*args, **kwargs):
    return need_oauth_authentication(identifier=oauth_identifier, *args, **kwargs)

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
    token = get_consumer_token(oauth_identifier)
    kwargs = {
        'server_url': token.server.server_url,
        'consumer_key': token.key,
        'consumer_secret': token.secret,
    }
    if is_oauth_authenticated(request, oauth_identifier):
        kwargs['token_key'] = request.session[oauth_identifier + '_oauth_token']
        kwargs['token_secret'] = request.session[oauth_identifier + '_oauth_token_secret']
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

class AuthenticationMiddleware(object):
    def process_request(self, request):
        """If some information are available in session about oauth token, 
        try to use it to authenticate to the BisonVert API, and provides a user
        in the request, as the `bvuser` parameter.

        """
        if is_oauth_authenticated(request, oauth_identifier):
            try:
                lib = get_lib(LibUsers, request)
                request.__class__.bvuser = lib.get_active_user()
            except Exception:
                request.__class__.bvuser = None
        else:
            request.__class__.bvuser = None
        return None

def bvauth(request):
    """Add `bvuser` to the context, if the user is logged in (determined by 
    the AuthenticationMiddleware from bv.libclient.ext.dj.
    
    If there is no `bvuser` attribute in the request, add `None` instead.
    """
    def get_user():
        if hasattr(request, 'bvuser'):
            return request.bvuser
        else:
            return None
    
    return {
        'bvuser': get_user(),
    }
