import os
os.environ.update([("CONFIG_MODE", "TESTS")])

import pytest
import asyncio


from project.database.models import init_db as idb

@pytest.fixture
def init_db():
    asyncio.run(idb())