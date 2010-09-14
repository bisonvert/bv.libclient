from bv.libclient.baselib import BaseLib
from bv.libclient.utils import json_unpack, ApiObject, dict_to_object, \
        dict_to_object_list, api_to_date, string_to_boolean

from bv.libclient.libtrips import Trip
from bv.libclient.libusers import User

class Rating(ApiObject):
    _class_keys = {
        'user': User,
        'from_user': User,
    }
    clean_creation_date = staticmethod(api_to_date)
    def get_mark(self):
        return self.mark

class TempRating(ApiObject):
    _class_keys = {
        'user1' : User,
        'user2': User, 
    }
    clean_end_date = staticmethod(api_to_date)
    clean_start_date = staticmethod(api_to_date)
    clean_date = staticmethod(api_to_date)
    clean_opened = staticmethod(string_to_boolean)

class LibRatings(BaseLib):
    _urls = {
        'ratings': '/ratings/',
        'tempratings': '/temp-ratings/',
    }
    
    @dict_to_object_list(Rating)
    @json_unpack()
    def get_given_ratings(self):
        return self.get_resource('ratings').get(path='given/')

    @dict_to_object_list(Rating)
    @json_unpack()
    def get_received_ratings(self):
        return self.get_resource('ratings').get(path='received/')

    @dict_to_object_list(TempRating)
    @json_unpack()
    def get_pending_ratings(self):
        return self.get_resource('tempratings').get()

    @dict_to_object(Rating)
    @json_unpack()
    def get_rating(self, id):
        return self.get_resource('ratings').get(path='%i/' % abs(int(id)))

    @dict_to_object(TempRating)
    @json_unpack()
    def get_temprating(self, id):
        return self.get_resource('tempratings').get(path='%i/' % abs(int(id)))
    
    def rate_user(self, rating_id, mark, comment):
        mark = abs(int(mark))
        if 0 <= mark <= 5:
            self.get_resource('ratings').post(**{
                'temprating_id':abs(int(rating_id)),
                'comment':comment, 
                'mark':mark
            })
        else:
            raise ValueError('mark must be between 0 and 5, both included;' \
                '%s given.' % mark)
