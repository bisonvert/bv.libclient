import json
import time
import datetime

"""A set of utilities relative to the lib module. (decorators, classes, callables)

"""

def unicode_to_dict(request):
    return dict([(key.__str__(),value) for key,value in request.items()])

def json_unpack(unpack_field='body'):
    """Unpack the result of a method (in json) to a python dict

    json_unpack can unpack a specific attribute of the response, 
    if exists and set in the unpack_field. 

    Default unpack field is "body"
    """
    def wrapper(func):
        def wrapped(*args, **kwargs):
            resp = func(*args, **kwargs)
            if unpack_field and hasattr(resp, unpack_field):
                resp = getattr(resp, unpack_field)
            return json.loads(resp)
        return wrapped
    return wrapper

def dict_to_object_func(dict, object):
    """Transform a dict into the specific object
    """
    if is_iterable(dict):
        return object(**unicode_to_dict(dict)) 
    else:
        return None

def dict_to_object_list_func(dict, object):
    """Transform a dict into the specific list of objects
    """
    return [dict_to_object_func(d, object) for d in dict]

def dict_to_object(object):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            return dict_to_object_func(func(*args, **kwargs), object)
        return wrapped
    return wrapper

def dict_to_object_list(object):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            return dict_to_object_list_func(func(*args, **kwargs), object)
        return wrapped
    return wrapper

#Model classes
class ApiObject:
    """Base Api Object.
    
    """
    _class_keys = {}
    def __init__(self, **kwargs):
        """Build an object thanks to the dict given in param.

        Set all attributes by using cleaner_* function when appropriate
        """
        for key, value in kwargs.items():
            cleaner = 'clean_'+key
            if hasattr(self, cleaner) and callable(getattr(self, cleaner)):
                cleaner_callable = getattr(self, cleaner)
                value = cleaner_callable(value)
            if is_iterable(value):
                if key in self._class_keys:
                    klass = self._class_keys[key]
                    value = klass(**unicode_to_dict(value))
            setattr(self, key, value) 

    def to_dict(self, init={}):
        """Return a dict based on the object itself.

        """
        keys = [item for item in dir(self) if not (callable(getattr(self, item)) or item.startswith(('__', '_')))]
        for key in keys:
            init[key] = getattr(self, key)
        return init
    
    def get(self, attr, default=False):
        return getattr(self, attr, default)

#convertors
def api_to_date(value):
    """Convert a date from YYY-MM-DD format to a real python date object.
    
    """
    return datetime.date(*time.strptime(value, '%Y-%m-%d')[:3])
    
def api_to_time(value):
    """Convert a date from  format to a real python datetime object.
    
    """
    if value is None:
        return None
    return datetime.time(*time.strptime(value, '%H:%M:%S')[3:6])
    
def date_to_api(value):
    """Convert a date in format DD/MM/YYYY to YYYY-MM-DD
    
    """
    splits = value.encode().split('/')
    splits.reverse()
    return "-".join(splits)

# Python 

def is_iterable(obj):
    try: 
        iter(obj)
    except: 
        return False
    else: 
        return True
