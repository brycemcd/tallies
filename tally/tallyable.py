"""
Core business logic
"""
from datetime import datetime


class TallyableNormalizer():
    """
    Normalizes a tallyable that was submitted into a standard format.

    I.e. "Alexa, I drank two beers" becomes 2 beer
    This is an extreme naive implementation
    """

    # NOTE: the left hand side is the lookup, the rhs is the normalized value
    MAPPER = {
        "beers": "beer",
        "ipa": "beer",
        "vodkas": "vodka",
        "glass of wine": "wine",
        "glasses of wine": "wine",
    }

    @classmethod
    def normalize(cls, tallyable):
        """
        Turns an utterance like "beers" into something more consistently
        trackable like "beer"

        :param tallyable: a string indicating what to tally
        :return: mapped tallyable: a normalized string
        """

        mapped = cls.MAPPER.get(tallyable)
        return mapped if mapped else tallyable


class Tallyable():
    """
    Handles stuff
    """

    def __init__(self, persistable, tallyable, normalizing_klass=TallyableNormalizer):
        """
        Instantiate the class with a persistable (Redis in this case)

        :param persistable: For now, it's an instance of Redis
        :param tallyable: a string indicating what to tally
        :param normalizing_klass: a class with a class method `normalize` that
            can turn a string into a normalized string (see default class docs)
        """

        self.persistable = persistable
        self.tallyable = normalizing_klass.normalize(tallyable)

    def add(self, dttm=None):
        """
        Adds a tally for a particular tallyable

        :param dttm: a dttm object indicating when the tallyable thing happened
        :return: Boolean value if the tallyable was added
        """
        if not dttm or type(dttm) != datetime:
            dttm = datetime.now()

        # mutate the datetime obj into a string that can be safely persisted
        dttm = dttm.isoformat()
        result = None

        try:
            result = self.persistable.lpush(self.tallyable, dttm)

        # Our persistence layer may not be available at the time
        # or the request to it is garbage
        except Exception as e:
            pass

        return result

    def get_tallies_for_tallyable(self, n=10):
        """
        Return the last n tallies and a total count for a tallyable

        :param tallyable: a string indicating the tallyable
        :param n: an int to indicate how many to return
        :return:
        """

        try:
            # get the last n items (the n most recently pushed) on the list
            dttms = self.persistable.lrange(self.tallyable, 0, (n-1))
            length = self.persistable.llen(self.tallyable)
        except Exception as e:
            dttms, length = [], 0

        return (dttms, length)