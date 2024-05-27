import pytest

from ascents import _init
from ascents._models import AscentDB


def test_database_already_exists_error(db: AscentDB) -> None:
    with pytest.raises(_init.DatabaseAlreadyExistsError):
        _init.init_ascent_db(db._database)
