from datetime import datetime, timedelta
import pytest
from unittest.mock import MagicMock, patch
from tally.tallyable import Tallyable, TallyableNormalizer, TallyablePersistence
from psycopg2 import IntegrityError

class TestTallyableNormalizer():

    @pytest.mark.parametrize("submitted, normalized", [
        ("beers", "beer"),
        ("ipa", "beer"),
        ("vodkas", "vodka"),
        ("glass of wine", "wine"),
        ("glasses of wine", "wine"),
        # If we haven't mapped it, just return the tallyable
        ("foo", "foo"),
    ])
    def test_normalizer(self, submitted, normalized):
        result = TallyableNormalizer.normalize(submitted)
        assert normalized == result

class TestTallyablePeristence():

    def test_save(self):
        with patch("utilities.db.DB") as db:
            instance = db.return_value
            instance.execute.return_value = True

            assert TallyablePersistence.save('foo', '2018-01-01', db) is True

        with patch("utilities.db.DB") as db:
            instance = db.return_value
            instance.execute.side_effect = IntegrityError("error!")

            assert TallyablePersistence.save('foo', '2018-01-01', db) is False

    def test_last_n(self):
        with patch("utilities.db.DB") as db:
            instance = db.return_value
            dttms = [ (datetime.now(), ) for _ in range(10) ]
            instance.fetch_records.return_value = dttms

            result = TallyablePersistence.last_n('foo', 10, db)
            assert type(result) == list
            assert type(result[0]) == datetime

        # NOTE: tests cases where:
        # 1. tallyable is legit, but nothing has been tallied
        # 2. tallyable is not in the list of tallyable_items
        with patch("utilities.db.DB") as db:
            instance = db.return_value
            instance.fetch_records.return_value = []

            result = TallyablePersistence.last_n('foo', 10, db)
            assert list == type(result)
            assert 0 == len(result)

    def test_cnt(self):
        # NOTE: tests cases where:
        # 1. tallyable is legit, but nothing has been tallied
        # 1. tallyable is legit, and count is > 0
        # 2. tallyable is not in the list of tallyable_items
        with patch("utilities.db.DB") as db:
            fake_count = 120
            instance = db.return_value
            instance.fetch_one.return_value = (fake_count, )

            result = TallyablePersistence.total_cnt('foo', db)
            assert fake_count == result

class TestTallyable():

    DEFAULT_TALLYABLE_THING = "tallyable_thing"

    @staticmethod
    def fake_persistable():
        persistable = MagicMock(spec=TallyablePersistence)
        persistable.save.return_value=True

        return persistable

    @staticmethod
    def fake_persistable_with_side_effect():
        persistable = MagicMock(spec=TallyablePersistence)

        return persistable

    @staticmethod
    def n_datetimes(n=10):
        arr = []
        for _ in range(n):
            arr.append(datetime.now().isoformat())
        return arr

    def test_init(self):
        obj = Tallyable(self.DEFAULT_TALLYABLE_THING)

        assert obj.tallyable == self.DEFAULT_TALLYABLE_THING

    testdata = [
        (True, "tallyable_thing", None, True),
        (True, "tallyable_thing", datetime.now(), True),
        (True, "tallyable_thing", "not a date!", True),
        (False, "tallyable_thing", None, False),
    ]
    @pytest.mark.parametrize("ret_val, tallyable_thing, dttm, expected", testdata)
    def test_add_tally(self, ret_val, tallyable_thing, dttm, expected):
        persistable = self.fake_persistable()
        persistable.save.return_value = ret_val

        obj = Tallyable(tallyable_thing, persistable_klass=persistable)

        if dttm and type(dttm) == datetime:
            result = obj.add(dttm)
            called_dttm = dttm.isoformat()
            persistable.save.assert_called_once_with(tallyable_thing,
                                                      called_dttm)
        else:
            result = obj.add()
            persistable.save.assert_called_once()

        assert result is expected


    @pytest.mark.current
    def test_get_tallies_for_tallyable(self):

        # NOTE: depends on the persistable_klass returning a list of dttms or
        # an empty list and a count >= 0
        with patch("unittest.mock.MagicMock") as pers:
            pers.spec = TallyablePersistence
            instance = pers.return_value
            # TODO: when persistable class is instantiated, use instance
            pers.last_n.return_value = self.n_datetimes(10)
            pers.total_cnt.return_value = 200

            obj = Tallyable(self.DEFAULT_TALLYABLE_THING, persistable_klass=pers)
            list_of_dttms, cnt = obj.get_tallies_for_tallyable()
            pers.last_n.assert_called_with(self.DEFAULT_TALLYABLE_THING, 10)
            pers.total_cnt.assert_called_with(self.DEFAULT_TALLYABLE_THING)
            # check the order is what I expect
            assert type(list_of_dttms) == list
            assert type(cnt) == int

