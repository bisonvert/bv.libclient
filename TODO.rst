bvlibbclient
============

* FIX django context processors and middlewares about login/out. (actually, we 
  cannot logout)
* Use ordering via api when needed
* Provide a django middleware to handle lib exceptions and display errors
* Separate django utils into more than one module. Maybe separating into a
  structure like this could be a good idea:
        
        dj/
        - middlewares.py
        - context_processors.py
        - decorators.py


