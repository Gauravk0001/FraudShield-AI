import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import Organization, User, UserRole, Transaction, RiskScore, Alert, Investigation

def test_database_schema_creation(tmp_path):
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Verify we can create an organization and user
    org = Organization(name="Test Financial Corp")
    session.add(org)
    session.commit()
    
    user = User(
        organization_id=org.id,
        email="analyst@test.com",
        full_name="Alice Analyst",
        hashed_password="hashed_pass_123",
        role=UserRole.FRAUD_ANALYST
    )
    session.add(user)
    session.commit()
    
    retrieved_user = session.query(User).filter_by(email="analyst@test.com").first()
    assert retrieved_user is not None
    assert retrieved_user.role == UserRole.FRAUD_ANALYST
    assert retrieved_user.organization.name == "Test Financial Corp"
    session.close()
