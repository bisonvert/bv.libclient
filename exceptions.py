class LibException(Exception):
    """Base exception class for the lib

    """
    pass

class ResourceDoesNotExist(LibException):
    """A requested resource does not exist.

    """
    pass

class ResourceAccessForbidden(LibException):
    """User is not alowed to do the requested operation

    """
    pass

class EditTripFormError(LibException):
    pass
