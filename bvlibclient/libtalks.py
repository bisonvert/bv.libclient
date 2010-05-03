from bvlibclient.baselib import BaseLib
from bvlibclient.utils import json_unpack, ApiObject, dict_to_object, \
        dict_to_object_list, api_to_datetime

from bvlibclient.libtrips import Trip
from bvlibclient.libusers import User
from bvlibclient.constants import DEFAULT_PAGINATION
from bvlibclient.exceptions import *

class Talk(ApiObject):
    _class_keys = {
        'trip': Trip, 
        'from_user': User,
    }

class Message(ApiObject):
    _class_keys = {
        'talk' : Talk,
    }
    clean_date = staticmethod(api_to_datetime)

    @property
    def user(self):
        """return the message user"""
        if self.from_user:
            return self.talk.from_user
        else:
            return self.talk.trip.user

    @property
    def to_user(self):
        """return the user for wich the messsage has been wrote"""
        if self.from_user:
            return self.talk.trip.user
        else:
            return self.talk.from_user

class LibTalks(BaseLib):
    _urls = {
        'talks': '/talks/',
    }
    
    @dict_to_object_list(Talk)
    @json_unpack()
    def list_talks(self, page=1, count=DEFAULT_PAGINATION, ordered_by='date'):
        """Return the list of talks for the authenticated user.

        """
        return  self.get_resource('talks').get(
                **self._get_pagination_params(page,count))

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

    @dict_to_object_list(Talk)
    @json_unpack()
    def list_talks_by_trip(self, trip_id):
        """Return a talk by its id."""
        return self.get_resource('talks').get(trip_id=trip_id)

    @dict_to_object(Talk)
    @json_unpack()
    def get_talk(self, id):
        """Return a talk by its id."""
        return self.get_resource('talks').get(path='%i/' % int(id))
    
    def talk_exists_for_trip(self, trip_id):
        """Check if a test exists or not, and return True or False, depending
        the case
        
        """
        if len(self.list_talks_by_trip(trip_id)) > 0:
            return True
        else:
            return False

    def delete_talk(self, id, message):
        """Delete a talk, with the explicative message.

        """
        self.get_resource('talks').put(path='%s/' % id, cancel='true',
                message=message)

    def create_talk(self, trip_id, message):
        """Initalize the conversation with an existing user.

        """
        return int(self.get_resource('talks').post(**{
            'trip_id':trip_id, 
            'message':message
        }).body)

    @dict_to_object_list(Message)
    @json_unpack()
    def list_talk_messages(self, talk_id, *args, **kwargs):
        """List all the messages in a talk

        """
        return self.get_resource('talks').get(path='%s/messages/' % talk_id)


    def count_messages(self, talk_id):
        """Count the number of talks
        
        """
        return int(self.get_resource('talks').get(path='%i/messages/count/' %
                                                  int(talk_id)).body)

    def add_message_to_talk(self, talk_id, message):
        """Add a message to an existing talk

        """
        self.get_resource('talks').post(path='%s/messages/' % talk_id, **{
            'message':message,
        })

