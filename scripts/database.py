from sqlalchemy import create_engine, Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)

class FormData(Base):
    __tablename__ = 'forms_data'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    form_json = Column(Text, nullable=False)
    created_at = Column(String(50), default=datetime.now().isoformat)

# Initialize SQLite database
engine = create_engine('sqlite:///patient_assessment.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def store_in_database(data):
    session = Session()
    try:
        # Validate required fields
        if not all([data.get('patient_name'), data.get('dob'), data.get('date')]):
            raise ValueError("Missing required fields in data")

        # Date conversion with error handling
        try:
            dob = datetime.strptime(data['dob'], '%m/%d/%Y').date()
            date = datetime.strptime(data['date'], '%m/%d/%Y').date()
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid date format: {str(e)}")

        # Rest of your existing database code...
        
    except Exception as e:
        session.rollback()
        print(f"Database error: {str(e)}")
    finally:
        session.close()