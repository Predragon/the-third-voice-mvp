# src/data/models.py
from datetime import datetime, timedelta
from peewee import *
import enum
import uuid
from ..core.config import settings

# Initialize database
database = SqliteDatabase(settings.DATABASE_PATH)

# Enums for constrained fields
class ContextType(enum.Enum):
    ROMANTIC = "romantic"
    COPARENTING = "coparenting"
    WORKPLACE = "workplace"
    FAMILY = "family"
    FRIEND = "friend"

class SentimentType(enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    UNKNOWN = "unknown"

class MessageType(enum.Enum):
    TRANSFORM = "transform"
    INTERPRET = "interpret"

# Base model
class BaseModel(Model):
    class Meta:
        database = database

# User model (replacing auth.users from Supabase)
class User(BaseModel):
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    email = CharField(unique=True)
    hashed_password = CharField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'users'

class Contact(BaseModel):
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    name = TextField()
    context = CharField(choices=[(ctx.value, ctx.value) for ctx in ContextType])
    user = ForeignKeyField(User, backref='contacts', on_delete='CASCADE')
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'contacts'

class Message(BaseModel):
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    contact = ForeignKeyField(Contact, backref='messages', on_delete='CASCADE')
    contact_name = TextField()
    type = CharField(choices=[(msg.value, msg.value) for msg in MessageType], default=MessageType.INTERPRET.value)
    original = TextField()
    result = TextField(null=True)
    sentiment = CharField(choices=[(sent.value, sent.value) for sent in SentimentType], null=True)
    emotional_state = TextField(null=True)
    model = TextField(null=True)
    healing_score = IntegerField(null=True, constraints=[Check('healing_score >= 0 AND healing_score <= 10')])
    user = ForeignKeyField(User, backref='messages', on_delete='CASCADE')
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'messages'

class Interpretation(BaseModel):
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    contact = ForeignKeyField(Contact, backref='interpretations', on_delete='CASCADE')
    contact_name = TextField()
    original_message = TextField()
    interpretation = TextField()
    interpretation_score = IntegerField(null=True, constraints=[Check('interpretation_score >= 0 AND interpretation_score <= 10')])
    model = TextField()
    user = ForeignKeyField(User, backref='interpretations', on_delete='CASCADE')
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'interpretations'

class AIResponseCache(BaseModel):
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    contact = ForeignKeyField(Contact, backref='ai_cache', on_delete='CASCADE')
    message_hash = TextField()
    context = TextField()
    response = TextField()
    healing_score = IntegerField(null=True, constraints=[Check('healing_score >= 0 AND healing_score <= 10')])
    model = TextField()
    sentiment = CharField(choices=[(sent.value, sent.value) for sent in SentimentType], null=True)
    emotional_state = TextField(null=True)
    user = ForeignKeyField(User, backref='ai_cache', on_delete='CASCADE')
    created_at = DateTimeField(default=datetime.now)
    expires_at = DateTimeField(default=lambda: datetime.now() + timedelta(days=7))
    
    class Meta:
        table_name = 'ai_response_cache'

class Feedback(BaseModel):
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user = ForeignKeyField(User, backref='feedback', on_delete='CASCADE')
    rating = IntegerField(constraints=[Check('rating >= 1 AND rating <= 5')])
    feedback_text = TextField(null=True)
    feature_context = TextField()
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'feedback'

class DemoUsage(BaseModel):
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_email = TextField()
    login_time = DateTimeField(default=datetime.now)
    ip_address = TextField(null=True)
    
    class Meta:
        table_name = 'demo_usage'

# List of all models for database operations
MODELS = [User, Contact, Message, Interpretation, AIResponseCache, Feedback, DemoUsage]
