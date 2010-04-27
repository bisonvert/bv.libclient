"""Tests for the Bison vert bvlibclient

"""
import unittest
import json
from mock import Mock

from bvlibclient.baselib import BvResource, BaseLib
from bvlibclient import LibTrips, LibRatings, LibTalks, \
    Trip, Rating, Talk, \
    ResourceDoesNotExist, ApiException, ResourceAccessForbidden, \
    EditTripFormError 

class HttpResponse:
    """HttpResponse mock

    """
    def __init__(self, body, status_int):
        self.body = body
        self.status_int = status_int

class BaseTestCase(unittest.TestCase):
    """
    We do not test the connection to the API here, but just that right methods 
    are called on our resource object.

    The connexion with oauth, and the request are currently made by restkit,
    and API calls are NOT tested here.

    """
    lib_class = BaseLib
    _return_types = {
        'single': {'title': 'value'},
        'collection': [{'title': 'value'}, {'title2': 'value2'}],
        'emptycollection': [],
        'emptysingle': {},
        'error': {'error': 'this is an error'},
        'ok': 'OK',
        'created': 'CREATED',
    }

    def setUp(self):
        """Set up the lib object, and inject it a mocked resource object.

        Then, in our tests, we will test that the right methods of this 
        resource object has been called.

        """
        self.lib = self.lib_class()

    def _mock_resource_method(self, method_name, return_type=None, 
            value=None, http_response=False, status_int=200):
        """Mock the get_resource method of the baselib.

        Make it return a json string, to be unpacked by the lib 
        """
        res = Mock(BvResource)()
       
        if value == None and return_type != None:
            value = json.dumps(self._return_types[return_type])
        if http_response == True:
            value = HttpResponse(body=value, status_int=status_int)
        
        self.lib.get_resource = Mock()
        if return_type != None or value != None or http_response:
            getattr(res, method_name).return_value = value 
            self.lib.get_resource.return_value = res
        return res

class BaseLibTests(BaseTestCase):
    def test_get_pagination_params(self):
        params = (
            ((1, 20), (0, 20)), 
            ((4, 43), (129, 43)),
            (('1', '20'), (0, 20)),
        )
        for (page, count), (assumed_start, assumed_count) in params: 
            assert self.lib._get_pagination_params(page, count) == {
                'start': assumed_start, 
                'count': assumed_count
            }

class TripsTests(BaseTestCase):
    """Tests of the trip lib.

    """
    lib_class = LibTrips
    _return_types = dict(BaseTestCase._return_types.items() + {
        'trip_search_offers': {'trip_demands': None, 'trip_offers': [{'title': 'value'}, {'title2': 'value2'}], 'trip': None},
        'trip_search_demands': {'trip_demands': [{'title': 'value'}, {'title2': 'value2'}], 'trip_offers': None, 'trip': None},
    }.items())

    def test_transform_dows(self):
        params = (
            ({}, {}),
            ({'dows': ['1', '3', '5', '6']}, {'dows': '1-3-5-6'}),
            ({'dows': [1, 3, 5, 6]}, {'dows': '1-3-5-6'}),
            ({'dows': [1, 3, 5, 6], 'akey': 'avalue'}, 
                {'dows': '1-3-5-6', 'akey': 'avalue'}),
        )
        for input_dict, expected_output in params:
            assert self.lib._transform_dows(input_dict) == expected_output

    def test_list_trips(self):
        # test that get method is called, json unpacked and object built
        res = self._mock_resource_method('get', 'collection')
        trips = self.lib.list_trips()
        assert trips[0].title == 'value'
        assert trips[1].title2 == 'value2'
        res.get.assert_called_with(count=20, start=0)
    
    def test_list_empty_trips(self): 
        # when an empty collection is returned, a empty list must be built
        res = self._mock_resource_method('get', 'emptycollection')
        assert self.lib.list_trips() == []
        res.get.assert_called_with(count=20, start=0)
    
    def test_count_trips(self):
        params = (
            ('20', 20),
            (15, 15),
        )
        for given, expected in params:
            # test that a string is converted to int
            res = self._mock_resource_method('get', value=given, http_response=True)
            assert expected == self.lib.count_trips()
       
    def test_get_trip(self):
        params = (
            ('7', '7/'),
            (9, '9/'),
        )
        for trip_id, path in params:
            res = self._mock_resource_method('get', 'single')
            trip = self.lib.get_trip(trip_id)
            assert trip.title == 'value'
            res.get.assert_called_with(path=path)

    def test_add_trip(self):
        params = (
            ({}, {}),
            ({'emptyvalue': '', 'anotheremptyvalue': u''}, {}),
            ({'akey': 'avalue', 'emptyvalue': '', 'anotheremptyvalue': u''}, {'akey': 'avalue'}),
        )
        for input_dict, expected_call in params:
            res = self._mock_resource_method('post','single')
            trip = self.lib.add_trip(**input_dict)
            res.post.assert_called_with(**expected_call)
        
        assert trip.title == 'value'

    def test_count_user_trip(self):
        params = (
            ('20', 20),
            (15, 15),
        )
        for given, expected in params:
            # test that a string is converted to int
            res = self._mock_resource_method('get', value=given, http_response=True)
            assert expected == self.lib.count_user_trips()

    def test_list_user_trips(self):
        res = self._mock_resource_method('get', 'collection')
        trips = self.lib.list_user_trips()
        assert trips[0].title == 'value'
        assert trips[1].title2 == 'value2'
        res.get.assert_called_with(count=20, start=0, path='mine/')
    
    def test_edit_trip(self):
        params = (
            (('20', {}), 
            ({'return_type':'single', 'http_response': True, 'status_int': 200}, 
                {'path': '20/'})),
            
            ((20, {'akey': 'avalue'}), 
            ({'return_type': 'single', 'http_response':True, 'status_int':200}, 
                {'path': '20/', 'akey': 'avalue'}))
        )

        for (id, input_dict), (mockkwargs, expected_call) in params:
            res = self._mock_resource_method('put', **mockkwargs)
            trip = self.lib.edit_trip(id, **input_dict)
            assert trip.title == 'value'
            res.put.assert_called_with(**expected_call)

    def test_edit_trip_error(self):
        res = self._mock_resource_method('put', 'error', status_int=500, http_response=True)
        self.assertRaises(EditTripFormError, self.lib.edit_trip, 1)
        res.put.assert_called_with(path='1/')
    
    def test_set_alert(self):
        res = self._mock_resource_method('put', 'single')
        self.lib.set_alert(7, False)
        res.put.assert_called_with(path='7/', alert=False)   
    
    def test_delete_trip(self):
        res = self._mock_resource_method('delete', 'single')
        self.lib.delete_trip(7)
        res.delete.assert_called_with(path='7/')        

    def test_search_trip(self):
        res = self._mock_resource_method('get', 'trip_search_demands')
        matching_results = self.lib.search_trip(**{
            'trip_type': '0', # 0 is for Offer. so we want to look up for maching demands
            'trip_id': '7',
            'date': '31/12/2010',
            'akey': 'avalue',
        })
        # Fixme: remove useless kwargs from the lib (eg. trip_id and trip_type)
        res.get.assert_called_with(path='7/', akey='avalue', is_demand=True, 
                trip_id='7', trip_type='0', date='2010-12-31')

        assert matching_results['trip_offers'] == []
        assert matching_results['trip'] == None
        assert matching_results['trip_demands'][0].title == 'value'
        assert matching_results['trip_demands'][1].title2 == 'value2'
        
        
    def test_get_cities(self):
        params = (
            ('city with spaces', 'city-with-spaces'),
            ('city', 'city'),
        )

        for value, expected_path in params:
            res = self._mock_resource_method('get', 'collection')
            self.lib.get_cities(value)
            res.get.assert_called_with(path='%s/' % expected_path)

    def test_get_cartypes(self):
        res = self._mock_resource_method('get', 'collection')
        cartypes = self.lib.get_cartypes()
        res.get.assert_called_with()

        assert cartypes[0].title == 'value'
        assert cartypes[1].title2 == 'value2'

class TalksTests(BaseTestCase):
    """Tests of the talks lib.

    """
    lib_class = LibTalks
    
    def test_list_talks(self):
        res = self._mock_resource_method('get', 'collection')
        talks = self.lib.list_talks()
        res.get.assert_called_with()

        assert talks[0].title == 'value'
        assert talks[1].title2 == 'value2'

    def test_get_talk(self):
        res = self._mock_resource_method('get', 'single')
        id = 1
        talk = self.lib.get_talk_by_id(id)
        res.get.assert_called_with(path='%i/' % int(id)) 

    def test_count_talks(self):
        res = self._mock_resource_method('get', value='1',http_response=True)
        assert self.lib.count_talks() == 1
        res.get.assert_called_with(path='count/')

    def test_validate_talk(self):
        res = self._mock_resource_method('put', 'ok')
        self.lib.validate_talk(7)
        res.put.assert_called_with(path='7/', validate='true')

    def test_delete_talk(self):
        res = self._mock_resource_method('put', 'ok')
        self.lib.delete_talk(7, 'my message')
        res.put.assert_called_with(path='7/', message='my message',
            cancel='true')

    def test_create_talk(self):
        creation_message = 'creation message'
        res = self._mock_resource_method('post', 'ok')
        self.lib.create_talk(7, creation_message)
        res.post.assert_called_with(trip_id=7, message=creation_message)

    def test_list_talk_messages(self):
        res = self._mock_resource_method('get', 'collection')
        talk_id = 7
        self.lib.list_talk_messages(talk_id)
        res.get.assert_called_with(path='%s/messages/' % talk_id)

    def test_count_talks(self):
        res = self._mock_resource_method('get', value='1',http_response=True)
        assert self.lib.count_messages(2) == 1
        res.get.assert_called_with(path='2/messages/count/')

    def test_add_message_to_talk(self):
        res = self._mock_resource_method('post', 'ok')
        talk_id = 7
        talk_message = 'my message'
        self.lib.add_message_to_talk(talk_id, talk_message)
        res.post.assert_called_with(path='%s/messages/' % talk_id, message=talk_message)

class TestLibRatings(BaseTestCase):
    lib_class = LibRatings

    def test_get_given_ratings(self):
        res = self._mock_resource_method('get', 'collection')
        ratings = self.lib.get_given_ratings()
        res.get.assert_called_with(path="given/")
        assert len(ratings) == 2
        assert ratings[0].title == 'value'
        assert ratings[1].title2 == 'value2'

    def test_get_received_ratings(self):
        res = self._mock_resource_method('get', 'collection')
        ratings = self.lib.get_received_ratings()
        res.get.assert_called_with(path="received/")
        assert len(ratings) == 2
        assert ratings[0].title == 'value'
        assert ratings[1].title2 == 'value2'

    def test_get_pending_ratings(self):
        res = self._mock_resource_method('get', 'collection')
        pendings = self.lib.get_pending_ratings()
        res.get.assert_called_with()
        assert len(pendings) == 2
        assert pendings[0].title == 'value'
        assert pendings[1].title2 == 'value2'

    def test_get_rating_by_id(self):
        res = self._mock_resource_method('get', 'single')

        values_ok = (7, '7')
        values_wrong = ("sept")

        for id in values_ok:
            rating = self.lib.get_rating_by_id(id)
            res.get.assert_called_with(path='7/')
            assert rating.title == 'value'

        for id in values_wrong:
            self.assertRaises(ValueError, self.lib.get_rating_by_id, id)

    def test_rate_user(self):
        res = self._mock_resource_method('post', 'single')

        values_ok = (
            ("1","a simple comment"),
            (1,"a simple comment"),
            (-4, "a simple comment"),
            ("-4", "a simple comment"),
        )

        values_wrong = (
            ("10", "a simple comment"),
            ("deux", "a simple comment"),
            (-10, "a simple comment"),
            ("-10", "a simple comment"),
        )
        
        for mark, comment in values_ok:
            self.lib.rate_user(1, mark, comment)
            res.post.assert_called_with(path='1/', 
                    comment=comment, mark=abs(int(mark)))

        for mark, comment in values_wrong:
            self.assertRaises(ValueError, self.lib.rate_user, 1, mark, comment)

if __name__ == '__main__':
    unittest.main()
