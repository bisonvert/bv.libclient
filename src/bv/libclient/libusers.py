from bv.libclient.baselib import BaseLib
from bv.libclient.utils import json_unpack, ApiObject, dict_to_object

class User(ApiObject):
    def is_authenticated(self):
        return True

class LibUsers(BaseLib):
    _urls = {
        'active_user': '/users/active/',
        'user':'/users/',
    }
    
    @dict_to_object(User)
    @json_unpack()
    def get_active_user(self):
        """Return information about the logged user."""
        resp =  self.get_resource('active_user').get()
        return resp
    
    @dict_to_object(User)
    @json_unpack()
    def get_user(self, user_id):
        resp = self.get_resource('user').get(path='%s/' % user_id)
        return resp
