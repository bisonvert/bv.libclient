class BvLibClientException(Exception):
    """Base exception class for the lib

    """
    pass

class ResourceDoesNotExist(BvLibClientException):
    """A requested resource does not exist.

    """
    pass

class ResourceAccessForbidden(BvLibClientException):
    """User is not alowed to do the requested operation

    """
    pass

class EditTripFormError(BvLibClientException):
    """The trip form is not valid
    
    """
    pass

class ApiException(BvLibClientException):
    """Querying the API has resulted as an exception
    
    """
    pass

class InputError(BvLibClientException):
    """An input error has been detected.

    """
    pass
