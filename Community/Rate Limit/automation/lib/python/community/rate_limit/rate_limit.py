"""
Author: Rich Koshak

Provides a class to implement Rate Limiting in Rules. This will ignore
any calls to run that take place within a certain amount of time after the last
one was called.

This class is related to Gatekeeper with the difference being that Gatekeeper
will execute all calls but spread them out and this class drops repeated calls.

Types
=====
    - RateLimit: Implements the Latch Design Pattern.

License
=======
Copyright (c) 2019 Contributors to the openHAB Scripters project
"""
from datetime import datetime, timedelta

class RateLimit(object):
    """
    Keeps a timestamp for when a new call to run is allowed to execute, ignoring
    any calls that take place before that time.
    """

    def __init__(self):
        """ Initializes the timestamp to now. """
        self.until = datetime.now()

    def run(self, func, days=0, hours=0, mins=0, secs=0, msecs=0):
        """
        If it has been long enough since the last time that run was called,
        execute the passed in func. Otherwise ignore the call.

        Arguments:
            - func: The lambda or function to call if allowed.
            - days: Defaults to 0, how many days to wait before allowing run to
            execute again.
            - hours: Defaults to 0, how many hours to wait before allowing run
            to execute again.
            - mins: Defaults to 0, how many minutes to wait before allowing run
            to execute again.
            - secs: Defaults to 0, how many seconds to wait before allowing run
            to execute again.
            - msecs: Defaults to 0, how many milliseconds to wait before
            allowing run to execute again.

            NOTE: The time arguments are additive. For example, to wait for 1
            day 30 minutes one would pass days=1, minutes=30. Floats are
            allowed.
        """
        now = datetime.now()
        if now >= self.until:
            self.until = now + timedelta(days=days, hours=hours, minutes=mins,
                                         seconds=secs, milliseconds=msecs)
            func()
