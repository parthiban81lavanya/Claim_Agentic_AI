import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Text,
    Boolean
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func

# ---------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
     "postgresql+psycopg2://postgres:password@localhost:5432/claims_db"
)  
#This is updated below for docker container access the db

# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql+psycopg2://postgres:password@host.docker.internal:5432/claims_db"
# )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ---------------------------------------------------
# COMMON BASE MODEL (Auto Timestamp)
# ---------------------------------------------------

class BaseModel:
    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now())

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now()
        )

# ---------------------------------------------------
# CLAIM TABLE
# ---------------------------------------------------

class Claim(Base, BaseModel):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)

    # -----------------------------
    # INPUT FEATURES (index.html)
    # -----------------------------

    total_claim_amount = Column(Float, nullable=False)
    insured_age = Column(Integer, nullable=False)
    policy_annual_premium = Column(Float, nullable=False)

    # HIGH / MEDIUM / LOW (store as string)
    incident_severity = Column(String(20), nullable=False)

    previous_claims_count = Column(Integer, default=0)

    hospital_risk_score = Column(Float, default=0.0)

    # -----------------------------
    # ML OUTPUTS
    # -----------------------------

    fraud_probability = Column(Float)
    risk_level = Column(String(20))

    # APPROVED / REJECTED / INVESTIGATION
    status = Column(String(50))

    # Final decision after HumanAgent
    final_decision = Column(String(50))

    # -----------------------------
    # HUMAN / QA FIELDS
    # -----------------------------

    needs_human_approval = Column(Boolean, default=False)

    rejected_reason = Column(Text, nullable=True)

# ---------------------------------------------------
# ADMIN USERS TABLE
# ---------------------------------------------------

class AdminUser(Base, BaseModel):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)
    is_superadmin = Column(Boolean, default=False)

# ---------------------------------------------------
# CREATE TABLES
# ---------------------------------------------------

def init_db():
    
    Base.metadata.create_all(bind=engine)