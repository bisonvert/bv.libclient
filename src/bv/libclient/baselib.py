from restkit import Resource, OAuthFilter
from restkit.util import oauth2
from restkit.errors import ResourceNotFound, Unauthorized, RequestError, RequestFailed
from bv.libclient.exceptions import ResourceAccessForbidden, \
        ResourceDoesNotExist, ApiException
from bv.libclient.utils import json_unpack
import httplib2

class BvResource(Resource):
    """A Bison Vert Resource

    """
    def request(self, *args, **kwargs):
        """Redefine the request method to raise our proper exception when
        needed, and not expose the underlying lib.

        """
        try:
            # baselib : lors d'un appel a request
            # lib -> get_resource
            # ex: libUser.get_active_user()
            return super(BvResource, self).request(*args, **kwargs)
        except Exception as e:
            
            print "Erreur au niveau de BvResource.request()"
            print e
            # for debugging purposes. FIXME
            raise e
#        except ResourceNotFound as e:
#            raise ResourceDoesNotExist(e.response)
#        except Unauthorized as e:
#            raise ResourceAccessForbidden(e.response)
#        except RequestError as e:
#            raise ApiException(e)

class BaseLib:
    _api_base_url = ''
    _resource_class = BvResource
    
    def __init__(self, server_url=None, consumer_key=None, consumer_secret=None, token_key=None, token_secret=None, filters=None):
        """Initialize the lib with http oauth client if provided
        
        """
        self.server_url = server_url
        if filters:
            self.set_filters(filters)
        else:
            if None in (token_key, token_secret):
                # we do not want an authenticated request.
                self._oauth = False
                self._filters = None
            else:
                consumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
                token= oauth2.Token(token_key, token_secret)
                self._filters = [OAuthFilter('*', consumer, token)]
                self._oauth = True
    
    def get_filters(self):
        """return the existing client for this instance of lib.

        """
        return getattr(self, '_filters', None)

    def set_filters(self, filters):
        self._filters = filters
        self._oauth = True
    
    def get_params(self):
        """Return the parameters needed to create a new lib instance.

        """
        return {
            'server_url': self.server_url,
            'filters': self.get_filters(),
        }

    def get_resource_name(self, path):
        """Return a complete URL from a key
        
        """
        return '%s%s%s' % (self.server_url, self._api_base_url, path)
    
    def get_resource(self, key=None, path=None, filters=None):
        """Return a restkit resource object
        
        """
        if key and key in self._urls:
            path = self._urls[key]
        try: 
            if filters == None:
                filters = self._filters
            return self._resource_class(self.get_resource_name(path), filters=filters)
        except RequestFailed as e:
            raise Exception(e.response.body)
    
    def _get_pagination_params(self, page, count):
        return {
            'start': int(page) * int(count) - int(count),
            'count': int(count)
        }

