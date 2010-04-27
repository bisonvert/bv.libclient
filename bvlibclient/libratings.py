from bvlibclient.baselib import BaseLib
from bvlibclient.utils import json_unpack, ApiObject, dict_to_object, \
        dict_to_object_list, api_to_date

from bvlibclient.libtrips import Trip
from bvlibclient.libusers import User

class Rating(ApiObject):
    _class_keys = {
        'user': User,
        'from_user': User,
    }
    clean_creation_date = staticmethod(api_to_date)

class TempRating(ApiObject):
    _class_keys = {
        'user1' : User,
        'user2': User, 
        'trip': Trip,
    }
    clean_end_date = staticmethod(api_to_date)

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
    def get_rating_by_id(self, id):
        return self.get_resource('ratings').get(path='%i/' % abs(int(id)))

    def rate_user(self, id, mark, comment):
        mark = abs(int(mark))
        if 0 < mark < 5:
            self.get_resource('ratings').post(path='%i/' % abs(int(id)),
                comment=comment, mark=mark)
        else:
            raise ValueError()
