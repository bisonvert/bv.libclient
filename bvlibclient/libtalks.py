from bvlibclient.baselib import BaseLib
from bvlibclient.utils import json_unpack, ApiObject, dict_to_object, \
        dict_to_object_list

from bvlibclient.libtrips import Trip
from bvlibclient.libusers import User
from bvlibclient.constants import DEFAULT_PAGINATION

class Talk(ApiObject):
    _class_keys = {
        'trip': Trip, 
        'user': User,
    }
    pass

class Message(ApiObject):
    _class_keys = {
        'talk' : Talk,
    }
    pass

class LibTalks(BaseLib):
    _urls = {
        'talks': '/talks/',
    }
    
    @dict_to_object_list(Talk)
    @json_unpack()
    def list_talks(self, page=1, count=DEFAULT_PAGINATION, ordered_by='date'):
        """Return the list of talks for the authenticated user.

        """
        return self.get_resource('talks').get()

    def count_talks(self):
        """Count the number of talks
        
        """
        return int(self.get_resource('talks').get(path='count/').body)
    
    def validate_talk(self, id):
        """The validation, for a talk is the fact to say "OK, all of this seems
        good, we just now have to ride". Internally, a temporary report is
        created.
        
        """
        self.get_resource('talks').put(path='%s/' % id, validate='true')

    @dict_to_object(Talk)
    @json_unpack()
    def get_talk_by_id(self, id):
        """Return a talk by its id."""
        return self.get_resource('talks').get(path='%i/' % int(id))
    
    def talk_exists(self, trip_id):
        """Check if a test exists or not, and return True or False, depending
        the case
        
        """
        try:
            self.create_talk_talk_by_id(id)
            return True
        except ResourceDoesNotExist:
            return False

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


    def count_messages(self, talk_id):
        """Count the number of talks
        
        """
        return int(self.get_resource('talks').get(path='%i/messages/count/' %
                                                  int(talk_id)).body)

    def add_message_to_talk(self, talk_id, message):
        """Add a message to an existing talk

        """
        self.get_resource('talks').post(path='%s/messages/' % talk_id, 
                message=message)

