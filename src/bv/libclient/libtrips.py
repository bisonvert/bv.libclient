# Internal lib imports
from bv.libclient.baselib import BaseLib
from bv.libclient.utils import ApiObject, json_unpack, date_to_api, api_to_date, \
         api_to_time, dict_to_object, dict_to_object_list, unicode_to_dict, \
         is_iterable, dict_to_object_list_func, dict_to_object_func, \
         api_to_datetime
from bv.libclient.exceptions import ResourceAccessForbidden, ResourceDoesNotExist, \
    EditTripFormError
from bv.libclient.libusers import User
from bv.libclient.constants import DEFAULT_PAGINATION

from restkit.errors import RequestFailed
from restkit.util import url_encode

# Python imports
import json

TRIP_OFFER = 0
TRIP_DEMAND = 1
TRIP_BOTH = 2
DOWS = (0,'Mon'),(1,'Tue'), (2,'Wed'), (3,'Thu'), (4,'Fri'), (5,'Sat'), (6,'Sun')


def format_dict2str(kwargs):
    dct = dict([(key, value) for key,value in kwargs.items() if not value == u'' and not value == [u'']])
    return url_encode(dct)


# Model Objects
class Offer(ApiObject):
    @property
    def checkpoints(self):
        return self.steps

class Demand(ApiObject):
    pass

class Trip(ApiObject):
    """Represents a python Trip object, to be manipulated by python views
    
    """
    _class_keys = {
        'user': User,
        'offer': Offer,
        'demand': Demand,
    }
    clean_date = staticmethod(api_to_date)
    clean_time = staticmethod(api_to_time)
    clean_creation_date = staticmethod(api_to_datetime)
    clean_modification_date = staticmethod(api_to_datetime)
    
    @property
    def trip_type(self):
        if getattr(self, 'offer', False) and getattr(self, 'demand', False):
            return TRIP_BOTH
        elif getattr(self, 'offer', False):
            return TRIP_OFFER
        elif getattr(self, 'demand', False):
            return TRIP_DEMAND

    @property
    def trip_type_name(self):
        if self.trip_type == 0:
            return 'Offer'
        elif self.trip_type == 1:
            return 'Demand'
        elif self.trip_type == 2:
            return 'Both'

    @property
    def print_dows(self):
        if hasattr(self, 'dows'):
            return u'-'.join([value for (key, value) in DOWS
                if key in self.dows])
            return "dows"
        else:
            return None

    def __unicode__(self):
        return u"%s - %s" % (self.departure_city, self.arrival_city)
        

class CarType(ApiObject):
    def __str__(self):
        return self.name

class City(ApiObject):
    pass


class LibTrips(BaseLib):
    _urls = {
        'trip': '/trips/', 
        'city': '/cities/',
        'search': '/trips/search/',
        'cartypes': '/cartypes/',
        'calculate_buffer': '/gis/calculate_buffer/',
        'ogcserver': '/gis/ogcserver/',
    }
    
    def _transform_dows(self, kwargs):
        """Serialize the dows

        """
        if kwargs.has_key('dows'):
            kwargs['dows'] = '-'.join([str(dow) for dow in kwargs['dows']])
        return kwargs

    @dict_to_object_list(Trip)
    @json_unpack()
    def list_trips(self, page=1, count=DEFAULT_PAGINATION, ordered_by='date'):
        """Return a list of trips, ordered by the "ordered_by" parameter
        
        """
        return self.get_resource('trip').get(**self._get_pagination_params(page, count))
    
    def count_trips(self):
        """return the number of trips registered on the server.
        
        """
        return int(self.get_resource('trip').get(path='count/').body_string())
       
    @dict_to_object(Trip) 
    @json_unpack()
    def get_trip(self, trip_id):
        """Return informations about a particular trip
        
        """
        return self.get_resource('trip').get(path='%s/' % trip_id)

    @dict_to_object(Trip)
    @json_unpack()  
    def add_trip(self, **kwargs):
        """Add a new trip
        
        """
        kwargs = self._transform_dows(kwargs)
        return self.get_resource('trip').post(payload=format_dict2str(kwargs))
   
    def count_user_trips(self):
        """Return the number of trips for the registred user (for pagination pupose)

        """
        return int(self.get_resource('trip').get(path='count_mine/').body_string())

    @dict_to_object_list(Trip)
    @json_unpack()
    def list_user_trips(self, page=1, count=DEFAULT_PAGINATION, ordered_by='date'):
        """List all the user trips.
        
        """
        return self.get_resource('trip').get(path='mine/', **self._get_pagination_params(page, count))
    

    def edit_trip(self, trip_id, **kwargs):
        """Send new informations about the trip to the API, and return the right
        response/error.
        
        """
        kwargs = self._transform_dows(kwargs)
        response = self.get_resource('trip').put(path='%s/' % trip_id, payload=format_dict2str(kwargs))
        if response.status_int == 200:
            return dict_to_object_func(json.loads(response.body_string()), Trip)
        else:
            raise EditTripFormError(json.loads(response.body_string()))
    
    def set_alert(self, trip_id, value):
        """Change the value of the alert for a specific trip.

        """
        return self.get_resource('trip').put(path="%s/" % trip_id, payload=format_dict2str({'alert':value}))

    def delete_trip(self, trip_id):
        """Delete a trip, or raise appropriate exceptions if needed.
        
        """
        resp = self.get_resource('trip').delete(path='%s/' % trip_id)

    def search_trip(self, **kwargs):
        """May be triggered by an AJAX call.
        kwargs contains json info to unpack
        But : it may not contain the "route" information which will trigger a bug
        """
        temp_results = self._search_trip(**kwargs)
        object = Trip

        return_dict = {}
        for key, value in temp_results.items():
            if key in ('trip_demands', 'trip_offers'):
                if value:
                    realvalue = [dict_to_object_func(dict, object) for dict in value]
                else:
                    realvalue = []
            elif key == 'trip':
                realvalue = dict_to_object_func(value, object)
            return_dict[key] = realvalue
        return return_dict
    
    @json_unpack()
    def _search_trip(self, **kwargs):
        """Find a trip using criterias. 
        
        Returns a json encoded list of trips. 
        
        """
        if 'date' in kwargs.keys():
            kwargs['date'] = date_to_api(kwargs['date'])
            
        if 'type' in kwargs.keys():
            trip_type = int(kwargs['type'])
        if 'trip_type' in kwargs.keys():
            trip_type = int(kwargs['trip_type'])
        
        if trip_type != None:
            if trip_type == TRIP_DEMAND:
                kwargs['is_demand'] = True
            if trip_type == TRIP_OFFER:
                kwargs['is_offer'] = True
        
        if 'trip_id' in kwargs and kwargs['trip_id']: 
            kwargs['path'] = '%s/' % kwargs['trip_id']

        # will trigger the server to search the trip
        return self.get_resource('search').get(**kwargs)
    
    @json_unpack()
    def get_cities(self, value):
        return self.get_resource('city').get(path='%s/' % value.replace(' ', '-'))
    
    @dict_to_object_list(CarType)
    @json_unpack()
    def get_cartypes(self):
        """Return the list of available cartypes from the server.

        """
        return self.get_resource('cartypes').get()

    @json_unpack()
    def calculate_buffer(self, params):
        return self.get_resource('calculate_buffer').get(**params)
   
    def ogcserver(self, params):
        return self.get_resource('ogcserver', filters=[]).get(**params).body_string()
