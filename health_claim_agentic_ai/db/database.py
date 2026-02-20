# 
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Text
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

# Recommended: Use environment variable
# export DATABASE_URL="postgresql+psycopg2://postgres:password@localhost:5432/claims_db"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:password@localhost:5432/claims_db"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,          # Set True for SQL debugging
    pool_pre_ping=True   # Helps avoid stale connections
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# --------------------------------------------------
# CLAIM TABLE MODEL
# --------------------------------------------------

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Inputs
    total_claim_amount = Column(Float, nullable=False)
    policy_annual_premium = Column(Float, nullable=False)
    insured_age = Column(Integer, nullable=False)
    incident_severity = Column(String(50), nullable=False)

    # ML Layer
    fraud_score = Column(Float)
    ml_model_version = Column(String(50), default="xgboost_v1")

    # QA Layer
    qa_notes = Column(Text)
    review_priority = Column(String(20))  # LOW | MEDIUM | HIGH

    # Human Review
    status = Column(
        String(50),
        default="PENDING_HUMAN_REVIEW"
    )

    human_decision = Column(Text)
    approved_by = Column(String(100))
    approved_at = Column(DateTime)

    # LLM Explainability
    llm_explanation = Column(Text)

    # Audit
    last_updated = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return (
            f"<Claim(id={self.id}, "
            f"amount={self.total_claim_amount}, "
            f"fraud_score={self.fraud_score}, "
            f"status={self.status})>"
        )


# --------------------------------------------------
# CREATE TABLES
# --------------------------------------------------

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Tables created successfully in PostgreSQL.")

# ###################################################################################### #
# from sqlalchemy import (
#     create_engine,
#     Column,
#     Integer,
#     Float,
#     String,
#     DateTime,
#     Text
# )
# from sqlalchemy.orm import declarative_base, sessionmaker
# from datetime import datetime

# #DATABASE_URL = "sqlite:///claims.db"
# DATABASE_URL = "postgresql://user:password@localhost:5432/claims_db"

# engine = create_engine(
#     DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     echo=False  # Turn True only for debugging
# )

# SessionLocal = sessionmaker(bind=engine)
# Base = declarative_base()


# class Claim(Base):
#     __tablename__ = "claims"

#     id = Column(Integer, primary_key=True, index=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     # Inputs
#     total_claim_amount = Column(Float, nullable=False)
#     policy_annual_premium = Column(Float, nullable=False)
#     insured_age = Column(Integer, nullable=False)
#     incident_severity = Column(String, nullable=False)

#     # ML Layer
#     fraud_score = Column(Float)
#     ml_model_version = Column(String, default="xgboost_v1")

#     # QA Layer
#     qa_notes = Column(Text)
#     review_priority = Column(String)  # LOW | MEDIUM | HIGH

#     # Human Review
#     status = Column(
#         String,
#         default="PENDING_HUMAN_REVIEW"
#     )

#     human_decision = Column(Text)
#     approved_by = Column(String)
#     approved_at = Column(DateTime)

#     # LLM Explainability
#     llm_explanation = Column(Text)

#     # Audit
#     last_updated = Column(
#         DateTime,
#         default=datetime.utcnow,
#         onupdate=datetime.utcnow
#     )

#     def __repr__(self):
#         return (
#             f"<Claim(id={self.id}, "
#             f"amount={self.total_claim_amount}, "
#             f"fraud_score={self.fraud_score}, "
#             f"status={self.status})>"
#         )


# Base.metadata.create_all(bind=engine)
