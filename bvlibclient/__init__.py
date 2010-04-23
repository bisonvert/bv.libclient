version_info = (0, 1, 0)
__version__ =  ".".join(map(str, version_info))

"""Official python lib to access the Bison Vert Carpooling webservice.

You can find more informations about the API at http://api.bisonvert.net/

"""

# Imports all things that have to be accessed from outside.
from bvlibclient.libtrips import LibTrips, Trip, Offer, Demand
from bvlibclient.libusers import LibUsers, User
from bvlibclient.libtalks import LibTalks
from bvlibclient.utils import unicode_to_dict 
from bvlibclient.exceptions import *
