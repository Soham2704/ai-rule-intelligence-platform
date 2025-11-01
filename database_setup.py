import sqlalchemy
from sqlalchemy import create_engine, Column, String, JSON, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# --- 1. Database Configuration ---
DB_NAME = "rules.db"
DB_PATH = os.path.join("rules_db", DB_NAME)
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create the directory if it doesn't exist to prevent errors
os.makedirs("rules_db", exist_ok=True)

# --- 2. SQLAlchemy Setup ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Use the modern SQLAlchemy 2.0 syntax for the base class
Base = declarative_base()

# --- 3. Define the Final, Professional Table Schemas ---

class Rule(Base):
    """The master table for all compliance rules, including all required metadata."""
    __tablename__ = "rules"
    id = Column(String, primary_key=True, index=True)
    city = Column(String, index=True)
    rule_type = Column(String, index=True)
    conditions = Column(JSON)
    entitlements = Column(JSON)
    notes = Column(Text)
    # --- FINAL UPGRADE: Added required metadata columns ---
    authority = Column(String)
    clause_no = Column(String)
    page = Column(String)

class Feedback(Base):
    """A table to store all human feedback, as required by the brief."""
    __tablename__ = "feedback"
    id = Column(String, primary_key=True, index=True)
    case_id = Column(String, index=True)
    project_id = Column(String, index=True)
    city = Column(String, index=True)
    feedback_type = Column(String) # "up" or "down"
    timestamp = Column(String)
    full_input = Column(JSON)
    full_output = Column(JSON)

class GeometryOutput(Base):
    """A table to store references to generated geometry files, as required by the brief."""
    __tablename__ = "geometry_outputs"
    id = Column(String, primary_key=True, index=True)
    case_id = Column(String, index=True, unique=True)
    project_id = Column(String, index=True)
    stl_path = Column(String)
    timestamp = Column(String)

class ReasoningOutput(Base):
    """A table to store the AI's reasoning and confidence for each run, as required by the brief."""
    __tablename__ = "reasoning_outputs"
    id = Column(String, primary_key=True, index=True)
    case_id = Column(String, index=True, unique=True)
    project_id = Column(String, index=True)
    rules_applied = Column(JSON)
    reasoning_summary = Column(Text)  # Detailed explanation
    clause_summaries = Column(JSON)  # NEW: Structured clause data
    confidence_score = Column(Float)
    confidence_level = Column(String)  # NEW: High/Moderate/Low
    confidence_note = Column(Text)  # NEW: Human-readable note
    timestamp = Column(String)

# --- 4. Main Execution Block to Create/Update the Database ---
def create_database():
    """
    This function creates the database and all required tables if they don't exist.
    """
    print(f"--- Creating/Updating database at '{DB_PATH}' ---")
    Base.metadata.create_all(bind=engine)
    print("--- Database and tables created/updated successfully. ---")

if __name__ == "__main__":
    create_database()

