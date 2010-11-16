===================================================================================
BisonVert LibClient: official lib to consume the REST API of the BisonVert's server
===================================================================================

**bv.libclient** is a simple lib client for the `BisonVert server`_ REST API.

It also includes features to ease the  *Oauth authentication* (needed by the BisonVert's server) 
for Django application (it uses django-oauthclient_).

See bv.client_ as a good example on how to use this API.

Embedding bv.libclient in a Django application
----------------------------------------------
Your best bet will be to see how bv.client_ works, as it is itself, a Django application.

Aside from this, remember that you will need configure your application with the
token identifier given by the server.
To procede, add BVCLIENT_OAUTH_APPID=<your_app_name> in you settings.py that will match this identifier
(see bv.libclient.ext.dj for more).


.. bv.libclient relies on `restkit <https://github.com/benoitc/restkit/>`_ to communicate with the REST api
.. check the api documentation at.

.. _bv.client: https://github.com/djcoin/bv.client
.. _BisonVert server: https://github.com/djcoin/bv.server
.. _django-oauthclient: https://github.com/djcoin/django-oauthclient
