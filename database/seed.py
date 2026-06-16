import os
import sys
from datetime import datetime, timedelta
from uuid import uuid4, UUID

# Add the parent directory to the path so we can import from database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Base, User, Session, Message, UploadedFile, DocumentChunk, SessionLocal, engine

def seed_database():
    """Seed the database with sample data."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Clear existing data (optional, for idempotent seeding)
        # Delete in reverse order of foreign key dependencies
        db.query(DocumentChunk).delete()
        db.query(UploadedFile).delete()
        db.query(Message).delete()
        db.query(Session).delete()
        db.query(User).delete()
        db.commit()
        
        print("Seeding database...")
        
        # 1. Create Users (parent of sessions)
        users = [
            User(
                id=UUID('11111111-1111-1111-1111-111111111111'),
                email="alice@example.com",
                created_at=datetime.utcnow() - timedelta(days=30)
            ),
            User(
                id=UUID('22222222-2222-2222-2222-222222222222'),
                email="bob@example.com",
                created_at=datetime.utcnow() - timedelta(days=15)
            ),
            User(
                id=UUID('33333333-3333-3333-3333-333333333333'),
                email="charlie@example.com",
                created_at=datetime.utcnow() - timedelta(days=7)
            )
        ]
        db.add_all(users)
        db.commit()
        print(f"Created {len(users)} users")
        
        # 2. Create Sessions (parent of messages and uploaded_files)
        sessions = [
            Session(
                id=UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
                user_id=UUID('11111111-1111-1111-1111-111111111111'),
                name="Project Planning",
                created_at=datetime.utcnow() - timedelta(days=5)
            ),
            Session(
                id=UUID('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
                user_id=UUID('11111111-1111-1111-1111-111111111111'),
                name="Research Notes",
                created_at=datetime.utcnow() - timedelta(days=3)
            ),
            Session(
                id=UUID('cccccccc-cccc-cccc-cccc-cccccccccccc'),
                user_id=UUID('22222222-2222-2222-2222-222222222222'),
                name="Meeting Summary",
                created_at=datetime.utcnow() - timedelta(days=1)
            )
        ]
        db.add_all(sessions)
        db.commit()
        print(f"Created {len(sessions)} sessions")
        
        # 3. Create Messages (child of sessions)
        messages = [
            Message(
                id=UUID('dddddddd-dddd-dddd-dddd-dddddddddddd'),
                session_id=UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
                role="user",
                content="Hello, can you help me plan my project timeline?",
                created_at=datetime.utcnow() - timedelta(days=5, hours=2)
            ),
            Message(
                id=UUID('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'),
                session_id=UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
                role="assistant",
                content="Of course! I'd be happy to help you plan your project timeline. Could you tell me more about the project scope and deadlines?",
                created_at=datetime.utcnow() - timedelta(days=5, hours=1, minutes=45)
            ),
            Message(
                id=UUID('ffffffff-ffff-ffff-ffff-ffffffffffff'),
                session_id=UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
                role="user",
                content="It's a web application with a 3-month deadline. We need user authentication, a dashboard, and reporting features.",
                created_at=datetime.utcnow() - timedelta(days=5, hours=1, minutes=30)
            ),
            Message(
                id=UUID('gggggggg-gggg-gggg-gggg-gggggggggggg'),
                session_id=UUID('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
                role="system",
                content="You are a research assistant specializing in scientific literature review.",
                created_at=datetime.utcnow() - timedelta(days=3, hours=1)
            ),
            Message(
                id=UUID('hhhhhhhh-hhhh-hhhh-hhhh-hhhhhhhhhhhh'),
                session_id=UUID('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
                role="user",
                content="Find recent papers about machine learning in healthcare diagnostics.",
                created_at=datetime.utcnow() - timedelta(days=3, hours=0, minutes=45)
            ),
            Message(
                id=UUID('iiiiiiii-iiii-iiii-iiii-iiiiiiiiiiii'),
                session_id=UUID('cccccccc-cccc-cccc-cccc-cccccccccccc'),
                role="user",
                content="Summarize the key decisions from today's meeting.",
                created_at=datetime.utcnow() - timedelta(days=1, hours=3)
            )
        ]
        db.add_all(messages)
        db.commit()
        print(f"Created {len(messages)} messages")
        
        # 4. Create UploadedFiles (child of sessions)
        uploaded_files = [
            UploadedFile(
                id=UUID('jjjjjjjj-jjjj-jjjj-jjjj-jjjjjjjjjjjj'),
                session_id=UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
                filename="project_spec.pdf",
                file_path="/uploads/project_spec.pdf",
                uploaded_at=datetime.utcnow() - timedelta(days=5, hours=0, minutes=30)
            ),
            UploadedFile(
                id=UUID('kkkkkkkk-kkkk-kkkk-kkkk-kkkkkkkkkkkk'),
                session_id=UUID('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
                filename="research_paper.docx",
                file_path="/uploads/research_paper.docx",
                uploaded_at=datetime.utcnow() - timedelta(days=3, hours=0, minutes=15)
            ),
            UploadedFile(
                id=UUID('llllllll-llll-llll-llll-llllllllllll'),
                session_id=UUID('cccccccc-cccc-cccc-cccc-cccccccccccc'),
                filename="meeting_notes.txt",
                file_path="/uploads/meeting_notes.txt",
                uploaded_at=datetime.utcnow() - timedelta(days=1, hours=2)
            )
        ]
        db.add_all(uploaded_files)
        db.commit()
        print(f"Created {len(uploaded_files)} uploaded files")
        
        # 5. Create DocumentChunks (child of uploaded_files)
        document_chunks = [
            DocumentChunk(
                id=UUID('mmmmmmmm-mmmm-mmmm-mmmm-mmmmmmmmmmmm'),
                uploaded_file_id=UUID('jjjjjjjj-jjjj-jjjj-jjjj-jjjjjjjjjjjj'),
                chunk_index=0,
                content="Project Specification Document\nVersion 1.0\n\nProject Overview: This document outlines the requirements for the new web application.",
                embedding=None,
                row_start=1,
                row_end=5
            ),
            DocumentChunk(
                id=UUID('nnnnnnnn-nnnn-nnnn-nnnn-nnnnnnnnnnnn'),
                uploaded_file_id=UUID('jjjjjjjj-jjjj-jjjj-jjjj-jjjjjjjjjjjj'),
                chunk_index=1,
                content="Functional Requirements:\n1. User authentication with email/password and OAuth\n2. Dashboard with key metrics visualization\n3. Reporting module with export capabilities",
                embedding=None,
                row_start=6,
                row_end=10
            ),
            DocumentChunk(
                id=UUID('oooooooo-oooo-oooo-oooo-oooooooooooo'),
                uploaded_file_id=UUID('jjjjjjjj-jjjj-jjjj-jjjj-jjjjjjjjjjjj'),
                chunk_index=2,
                content="Technical Requirements:\n- Backend: Python with FastAPI\n- Frontend: React with TypeScript\n- Database: PostgreSQL with pgvector\n- Deployment: Docker on AWS",
                embedding=None,
                row_start=11,
                row_end=15
            ),
            DocumentChunk(
                id=UUID('pppppppp-pppp-pppp-pppp-pppppppppppp'),
                uploaded_file_id=UUID('kkkkkkkk-kkkk-kkkk-kkkk-kkkkkkkkkkkk'),
                chunk_index=0,
                content="Machine Learning in Healthcare: A Review\nAbstract: This paper reviews recent advances in machine learning applications for healthcare diagnostics.",
                embedding=None,
                row_start=1,
                row_end=4
            ),
            DocumentChunk(
                id=UUID('qqqqqqqq-qqqq-qqqq-qqqq-qqqqqqqqqqqq'),
                uploaded_file_id=UUID('kkkkkkkk-kkkk-kkkk-kkkk-kkkkkkkkkkkk'),
                chunk_index=1,
                content="Key Findings:\n1. Deep learning models achieve 95% accuracy in detecting diabetic retinopathy from retinal images.\n2. Natural language processing can extract clinical insights from electronic health records.",
                embedding=None,
                row_start=5,
                row_end=8
            ),
            DocumentChunk(
                id=UUID('rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr'),
                uploaded_file_id=UUID('llllllll-llll-llll-llll-llllllllllll'),
                chunk_index=0,
                content="Meeting Notes - Project Kickoff\nDate: 2024-01-15\nAttendees: Alice, Bob, Charlie\n\nAgenda:\n1. Project goals and timeline\n2. Team roles and responsibilities\n3. Technology stack decisions",
                embedding=None,
                row_start=1,
                row_end=7
            ),
            DocumentChunk(
                id=UUID('ssssssss-ssss-ssss-ssss-ssssssssssss'),
                uploaded_file_id=UUID('llllllll-llll-llll-llll-llllllllllll'),
                chunk_index=1,
                content="Decisions Made:\n1. Project deadline set for April 15, 2024\n2. Alice will lead backend development\n3. Bob will handle frontend implementation\n4. Charlie will manage deployment and DevOps",
                embedding=None,
                row_start=8,
                row_end=12
            ),
            DocumentChunk(
                id=UUID('tttttttt-tttt-tttt-tttt-tttttttttttt'),
                uploaded_file_id=UUID('llllllll-llll-llll-llll-llllllllllll'),
                chunk_index=2,
                content="Action Items:\n1. Alice: Set up database schema by next week\n2. Bob: Create wireframes for dashboard\n3. Charlie: Configure CI/CD pipeline\n\nNext meeting: Monday, January 22, 10:00 AM",
                embedding=None,
                row_start=13,
                row_end=18
            )
        ]
        db.add_all(document_chunks)
        db.commit()
        print(f"Created {len(document_chunks)} document chunks")
        
        print("Database seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == '__main__':
    seed_database()