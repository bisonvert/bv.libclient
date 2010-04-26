from bvlibclient.baselib import BaseLib
from bvlibclient.utils import json_unpack, ApiObject, dict_to_object, \
        dict_to_object_list

from bvlibclient.libtrips import Trip
from bvlibclient.libusers import User

class Rating(ApiObject):
    _class_keys = {
        'user': User,
        'from_user': User,
    }
    pass

class TempRating(ApiObject):
    _class_keys = {
        'talk' : Talk,
    }
    pass

class LibTalks(BaseLib):
    _urls = {
        'talks': '/talks/',
        'user':'/users/',
    }
    
    @dict_to_object_list(Talk)
    @json_unpack()
    def list_talks(self):
        """Return the list of talks for the authenticated user.

        """
        return self.get_resource('talks').get()
    
    def validate_talk(self, id):
        """The validation, for a talk is the fact to say "OK, all of this seems
        good, we just now have to ride. Internally, a temporary report is
        created.
        
        """
        self.get_resource('talks').put(path='%s/' % id, validate='true')

    def delete_talk(self, id, message):
        """Delete a talk, with the explicative message.

        """
        self.get_resource('talks').put(path='%s/' % id, cancel='true',
                message=message)

    def create_talk(self, trip_id, message):
        """Initalize the conversation with an existing user.

        If the talk does not exist yet, create it for the purpose.
        
        """
        self.get_resource('talks').post(trip_id=trip_id, message=message)

    @dict_to_object_list(Message)
    @json_unpack()
    def list_talk_messages(self, talk_id, *args, **kwargs):
        """List all the messages in a talk

        """
        return self.get_resource('messages').get(path='%s/messages/' % talk_id)

    def add_message_to_talk(self, talk_id, message):
        """Add a message to an existing talk

        """
        self.get_resource('messages').post(path='%s/messages/' % talk_id, 
                message=message)

