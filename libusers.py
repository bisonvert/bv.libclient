from libclient.baselib import BaseLib
from libclient.utils import json_unpack, ApiObject, dict_to_object

class User(ApiObject):
    pass

class LibUsers(BaseLib):
    _urls = {
        'active_user': '/users/active/',
        'user':'/users/',
    }
    
    @dict_to_object(User)
    @json_unpack()
    def get_active_user(self):
        """Return information about the active and logged user.
        
        """
        return self.get_resource('active_user').get()
    
    @dict_to_object(User)
    @json_unpack()
    def get_user(self, user_id):
        return self.get_resource('user').get(path='%s/' % user_id)
