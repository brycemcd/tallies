"""
Core business logic
"""
from datetime import datetime
from utilities.db import DB
from psycopg2 import IntegrityError


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

class TallyablePersistence:
    """
    A small abstraction for storing tallyables
    """

    # TODO: refactor tallyable and db_klass out of the method calls

    @staticmethod
    def save(tallyable, dttm, db_klass=DB):
        try:
            db = db_klass()
            db.execute("""
                INSERT INTO tallies (tallyable_item, tally_dttm)
                VALUES ((SELECT id
                        FROM tallyable_items
                        WHERE tallyable_item = %s), %s)
            """, (tallyable, dttm))
            # NOTE `execute` always returns None
            return True
        except IntegrityError:
            return False

    @staticmethod
    def last_n(tallyable, n, db_klass=DB):
        db = db_klass()
        records = db.fetch_records("""
            SELECT
                tally_dttm
            FROM tallies
            WHERE tallyable_item = (
              SELECT id
              FROM tallyable_items
              WHERE tallyable_item = %s
            )
            LIMIT %s
        """, (tallyable, n))

        return [record[0] for record in records]

    @staticmethod
    def total_cnt(tallyable, db_klass=DB):
        db = db_klass()
        cnt = db.fetch_one("""
            SELECT
                COUNT(*) AS cnt
            FROM tallies
            WHERE tallyable_item = (
              SELECT id
              FROM tallyable_items
              WHERE tallyable_item = %s
            )
        """, (tallyable,))

        return cnt[0]


class Tallyable():
    """
    Handles stuff
    """

    def __init__(self, tallyable, persistable_klass=TallyablePersistence, normalizing_klass=TallyableNormalizer):
        """
        Instantiate the class with a persistable (Redis in this case)

        :param persistable: For now, it's an instance of Redis
        :param tallyable: a string indicating what to tally
        :param normalizing_klass: a class with a class method `normalize` that
            can turn a string into a normalized string (see default class docs)
        """

        self.tallyable = normalizing_klass.normalize(tallyable)
        self.persistable = persistable_klass

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

        result = self.persistable.save(self.tallyable, dttm)

        return result

    def get_tallies_for_tallyable(self, n=10):
        """
        Return the last n tallies and a total count for a tallyable

        :param n: an int to indicate how many to return
        :return: tuple of last n datetimes and total count of specific tallyable
        """

        return self.persistable.last_n(self.tallyable, n),\
               self.persistable.total_cnt(self.tallyable)