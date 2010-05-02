from restkit import Resource, oauth2, OAuthFilter
from restkit.errors import ResourceNotFound, Unauthorized, RequestError, RequestFailed
from bvlibclient.exceptions import ResourceAccessForbidden, \
        ResourceDoesNotExist, ApiException
from bvlibclient.utils import json_unpack
import httplib2

class BvResource(Resource):
    """A Bison Vert Resource

    """
    def request(self, method, path=None, payload=None, headers=None, **params):
        """Redefine the request method to raise our proper exception when
        needed, and not expose the underlying lib.

        """
        try:
            return super(BvResource, self).request(method, path=path, 
                payload=payload, headers=headers, **params)
        except ResourceNotFound as e:
            raise ResourceDoesNotExist(e.response)
        except Unauthorized as e:
            raise ResourceAccessForbidden(e.response)
        except RequestError as e:
            raise ApiException(e)

class BaseLib:
    _api_base_url = '/api'
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
                self._filters = [OAuthFilter(('*', consumer, token))]
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
    
    def get_resource(self, key=None, path=None):
        """Return a restkit resource object
        
        """
        if key and key in self._urls:
            path = self._urls[key]
        try:  
            return self._resource_class(self.get_resource_name(path), filters=self._filters)
        except RequestFailed as e:
            raise Exception(e.response.body)
    
    def _get_pagination_params(self, page, count):
        return {
            'start': int(page) * int(count) - int(count),
            'count': int(count)
        }

