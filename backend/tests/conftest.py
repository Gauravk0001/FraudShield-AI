import os
os.environ["ENVIRONMENT"] = "testing"
os.environ["DB_TYPE"] = "sqlite"

import pytest
from app.core.database import Base, engine

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

