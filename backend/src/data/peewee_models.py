# backend/src/data/peewee_models.py
"""
Peewee database models for The Third Voice AI
SQLite-based models with proper foreign key relationships
"""

from datetime import datetime, timedelta
from peewee import *
from contextlib import contextmanager
import uuid
import os

from ..core.config import settings


# Initialize database
database = SqliteDatabase(settings.DATABASE_PATH)


class BaseModel(Model):
    """Base model with common configuration"""
    class Meta:
        database = database


class User(BaseModel):
    """User account model"""
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    email = CharField(unique=True, index=True)
    hashed_password = CharField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'users'


class Contact(BaseModel):
    """Contact model for people user communicates with"""
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    name = TextField()
    context = CharField()  # Will store enum values as strings
    user_id = CharField(index=True)  # Reference to user (can be demo user ID)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'contacts'
        indexes = (
            # Composite index for user queries
            (('user_id', 'created_at'), False),
        )


class Message(BaseModel):
    """Message processing history"""
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    contact_id = CharField(index=True)
    contact_name = TextField()
    type = CharField()  # 'transform' or 'interpret'
    original = TextField()
    result = TextField(null=True)
    sentiment = CharField(null=True)
    emotional_state = TextField(null=True)
    model = TextField(null=True)
    healing_score = IntegerField(null=True)
    user_id = CharField(index=True)
    created_at = DateTimeField(default=datetime.now, index=True)
    
    class Meta:
        table_name = 'messages'
        indexes = (
            # Composite indexes for common queries
            (('contact_id', 'user_id'), False),
            (('user_id', 'created_at'), False),
        )


class AIResponseCache(BaseModel):
    """Cache for AI responses to avoid duplicate processing"""
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    contact_id = CharField(index=True)
    message_hash = CharField(index=True)
    context = TextField()
    response = TextField()
    healing_score = IntegerField(null=True)
    model = TextField()
    sentiment = CharField(null=True)
    emotional_state = TextField(null=True)
    user_id = CharField(index=True)
    created_at = DateTimeField(default=datetime.now)
    expires_at = DateTimeField(default=lambda: datetime.now() + timedelta(days=7), index=True)
    
    class Meta:
        table_name = 'ai_response_cache'
        indexes = (
            # Composite index for cache lookups
            (('contact_id', 'message_hash', 'user_id'), False),
            # Index for cleanup
            (('expires_at',), False),
        )


class Feedback(BaseModel):
    """User feedback collection"""
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = CharField(index=True)
    rating = IntegerField()  # 1-5 stars
    feedback_text = TextField(null=True)
    feature_context = TextField()  # Which feature the feedback is about
    created_at = DateTimeField(default=datetime.now, index=True)
    
    class Meta:
        table_name = 'feedback'


class DemoUsage(BaseModel):
    """Track demo user sessions for analytics"""
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_email = TextField()
    login_time = DateTimeField(default=datetime.now, index=True)
    ip_address = TextField(null=True)
    
    class Meta:
        table_name = 'demo_usage'


# All models for database operations
MODELS = [User, Contact, Message, AIResponseCache, Feedback, DemoUsage]


@contextmanager
def get_db_context():
    """Context manager for database connections"""
    try:
        database.connect(reuse_if_open=True)
        yield database
    except Exception as e:
        print(f"Database error: {e}")
        raise
    finally:
        if not database.is_closed():
            database.close()


def create_tables():
    """Create all database tables"""
    try:
        with get_db_context():
            database.create_tables(MODELS, safe=True)
            print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


def drop_tables():
    """Drop all database tables (for development)"""
    try:
        with get_db_context():
            database.drop_tables(MODELS, safe=True)
            print("🗑️ Database tables dropped")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")


def reset_database():
    """Reset database (drop and recreate tables)"""
    print("🔄 Resetting database...")
    drop_tables()
    create_tables()
    print("✅ Database reset complete")


def get_database_info():
    """Get database information"""
    try:
        with get_db_context():
            info = {
                "database_path": settings.DATABASE_PATH,
                "database_size": os.path.getsize(settings.DATABASE_PATH) if os.path.exists(settings.DATABASE_PATH) else 0,
                "tables": []
            }
            
            # Get table info
            for model in MODELS:
                try:
                    count = model.select().count()
                    info["tables"].append({
                        "name": model._meta.table_name,
                        "count": count
                    })
                except:
                    info["tables"].append({
                        "name": model._meta.table_name,
                        "count": 0
                    })
            
            return info
    except Exception as e:
        return {"error": str(e)}


def migrate_database():
    """Handle database migrations"""
    # This is where you'd add migration logic
    # For now, just ensure tables exist
    create_tables()


# Initialize database on import
if __name__ == "__main__":
    create_tables()
