import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["ENVIRONMENT"] = "testing"
os.environ["DB_TYPE"] = "sqlite"

# Use dedicated test database so pytest never drops demo/dev database
test_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "test_fraudshield.db")).replace("\\", "/")
os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{test_db_path}"

import pytest
from app.core.database import Base, engine

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

