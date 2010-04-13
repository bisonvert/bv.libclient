"""Tests for the Bison vert libclient

"""
import unittest
import json
from mock import Mock

from libclient.baselib import BvResource, BaseLib
from libclient import LibTrips, Trip, EditTripFormError

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
        'collection': [{'title1': 'value'}, {'title2': 'value2'}],
        'emptycollection': [],
        'emptysingle': {},
        'error': {'error': 'this is an error'},
        'trip_search_offers': {'trip_demands': None, 'trip_offers': [{'title1': 'value'}, {'title2': 'value2'}], 'trip': None},
        'trip_search_demands': {'trip_demands': [{'title1': 'value'}, {'title2': 'value2'}], 'trip_offers': None, 'trip': None},
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
            self.assertEqual(self.lib._get_pagination_params(page, count), 
                {'start': assumed_start, 'count': assumed_count})

class TripsTests(BaseTestCase):
    """Tests of the trip lib.

    """
    lib_class = LibTrips

    def test_transform_dows(self):
        params = (
            ({}, {}),
            ({'dows': ['1', '3', '5', '6']}, {'dows': '1-3-5-6'}),
            ({'dows': [1, 3, 5, 6]}, {'dows': '1-3-5-6'}),
            ({'dows': [1, 3, 5, 6], 'akey': 'avalue'}, 
                {'dows': '1-3-5-6', 'akey': 'avalue'}),
        )
        for input_dict, expected_output in params:
            self.assertEqual(self.lib._transform_dows(input_dict), expected_output)

    def test_list_trips(self):
        # test that get method is called, json unpacked and object built
        res = self._mock_resource_method('get', 'collection')
        trips = self.lib.list_trips()
        self.assertEqual(trips[0].title1, 'value')
        self.assertEqual(trips[1].title2, 'value2')
        res.get.assert_called_with(count=20, start=0)
    
    def test_list_empty_trips(self): 
        # when an empty collection is returned, a empty list must be built
        res = self._mock_resource_method('get', 'emptycollection')
        self.assertEqual(self.lib.list_trips(), [], 'must return an empty list')
        res.get.assert_called_with(count=20, start=0)
    
    def test_count_trips(self):
        params = (
            ('20', 20),
            (15, 15),
        )
        for given, expected in params:
            # test that a string is converted to int
            res = self._mock_resource_method('get', value=given, http_response=True)
            self.assertEqual(expected, self.lib.count_trips())
       
    def test_get_trip(self):
        params = (
            ('7', '7/'),
            (9, '9/'),
        )
        for trip_id, path in params:
            res = self._mock_resource_method('get', 'single')
            trip = self.lib.get_trip(trip_id)
            self.assertEqual(trip.title, 'value')
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
        
        self.assertEqual(trip.title, 'value')

    def test_count_user_trip(self):
        params = (
            ('20', 20),
            (15, 15),
        )
        for given, expected in params:
            # test that a string is converted to int
            res = self._mock_resource_method('get', value=given, http_response=True)
            self.assertEqual(expected, self.lib.count_user_trips())

    def test_list_user_trips(self):
        res = self._mock_resource_method('get', 'collection')
        trips = self.lib.list_user_trips()
        self.assertEqual(trips[0].title1, 'value')
        self.assertEqual(trips[1].title2, 'value2')
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
            self.assertEqual(trip.title, 'value')
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

        self.assertEqual(matching_results['trip_offers'], [])
        self.assertEqual(matching_results['trip'], None)
        self.assertEqual(matching_results['trip_demands'][0].title1, 'value')
        self.assertEqual(matching_results['trip_demands'][1].title2, 'value2')
        
        
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

        self.assertEqual(cartypes[0].title1, 'value')
        self.assertEqual(cartypes[1].title2, 'value2')




if __name__ == '__main__':
    unittest.main()
