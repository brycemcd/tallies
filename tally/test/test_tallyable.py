from datetime import datetime, timedelta
import pytest
from unittest.mock import MagicMock
from tally.tallyable import Tallyable

class TestTallyable():

    DEFAULT_TALLYABLE_THING = "tallyable_thing"

    @staticmethod
    def fake_persistable():
        persistable = MagicMock()
        persistable.lpush = MagicMock(return_value=True)

        return persistable

    @staticmethod
    def fake_persistable_with_side_effect():
        persistable = MagicMock()
        persistable.lpush = MagicMock(side_effect=KeyError('foo'))
        persistable.llen = MagicMock(side_effect=KeyError('foo'))

        return persistable

    @staticmethod
    def n_datetimes(n=10):
        arr = []
        for _ in range(n):
            arr.append(datetime.now().isoformat())
        return arr

    def test_init(self):
        persistable = MagicMock()
        obj = Tallyable(persistable)

        assert obj.persistable is not None

    testdata = [
        (True, "tallyable_thing", None, True),
        (True, "tallyable_thing", datetime.now(), True),
        (True, "tallyable_thing", "not a date!", True),
        (False, "tallyable_thing", None, None),
    ]

    @pytest.mark.parametrize("golden_path, tallyable_thing, dttm, expected", testdata)
    def test_add_tally(self, golden_path, tallyable_thing, dttm, expected):
        if golden_path:
            persistable = self.fake_persistable()
        else:
            persistable = self.fake_persistable_with_side_effect()

        obj = Tallyable(persistable)

        if dttm and type(dttm) == datetime:
            result = obj.add(tallyable_thing, dttm)
            called_dttm = dttm.isoformat()
            persistable.lpush.assert_called_once_with(tallyable_thing,
                                                      called_dttm)
        else:
            result = obj.add(tallyable_thing)
            persistable.lpush.assert_called_once()

        assert result is expected


    #NOTE: I'm still trying to come up with a good way to do iteration tests
    testdata = [
        ("golden_path"),
        # if a key doesn't exist, then redis returns an empty list in python
        ("key_not_exists"),
        ("db_not_available")
    ]

    @pytest.mark.parametrize("test_type", testdata)
    def test_get_tallies_for_tallyable(self, test_type):

        persistable = self.fake_persistable()

        dttms = []
        if test_type == "golden_path":
            dttms = self.n_datetimes()
        elif test_type == "key_not_exists":
            dttms = []

        persistable.lrange.return_value = dttms
        persistable.llen.return_value = len(dttms)

        if test_type == "db_not_available":
            persistable = self.fake_persistable_with_side_effect()
            persistable.lrange.return_value = dttms
            persistable.llen.return_value = len(dttms)

        obj = Tallyable(persistable)

        assert obj.get_tallies_for_tallyable(self.DEFAULT_TALLYABLE_THING) == (dttms, len(dttms))
        persistable.lrange.assert_called_once()
        persistable.llen.assert_called_once()
