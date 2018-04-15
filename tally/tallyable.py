"""
Core business logic
"""
from datetime import datetime


class Tallyable():
    """
    Handles stuff
    """

    def __init__(self, persistable):
        """
        Instantiate the class with a persistable (Redis in this case)

        :param persistable: For now, it's an instance of Redis
        """

        self.persistable = persistable

    def add(self, tallyable, dttm=None):
        """
        Adds a tally for a particular tallyable

        :param tallyable: a string indicating what to tally
        :param dttm: a dttm object indicating when the tallyable thing happened
        :return: Boolean value if the tallyable was added
        """
        if not dttm or type(dttm) != datetime:
            dttm = datetime.now()

        # mutate the datetime obj into a string that can be safely persisted
        dttm = dttm.isoformat()
        result = None

        try:
            result = self.persistable.lpush(tallyable, dttm)

        # Our persistence layer may not be available at the time
        # or the request to it is garbage
        except Exception as e:
            pass

        return result

    def get_tallies_for_tallyable(self, tallyable, n=10):
        """
        Return the last n tallies and a total count for a tallyable

        :param tallyable: a string indicating the tallyable
        :param n: an int to indicate how many to return
        :return:
        """

        try:
            # get the last n items (the n most recently pushed) on the list
            dttms = self.persistable.lrange(tallyable, (n*-1), -1)
            length = self.persistable.llen(tallyable)
        except Exception as e:
            dttms, length = [], 0

        return (dttms, length)