from fastapi import FastAPI
from peewee import SqliteDatabase, Model, IntegerField, TextField, ForeignKeyField, DateTimeField
from peewee import JOIN
from datetime import datetime

app = FastAPI()
db = SqliteDatabase('/home/thirdvoice/the-third-voice-mvp/thirdvoice.db')

class Messages(Model):
    id = IntegerField(primary_key=True)
    sender_id = IntegerField()
    receiver_id = IntegerField()
    content = TextField()
    sent_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = 'messages'

class AIResponseCache(Model):
    id = IntegerField(primary_key=True)
    message_id = ForeignKeyField(Messages, backref='ai_responses')
    ai_response = TextField()
    generated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = 'ai_response_cache'

@app.get("/messages")
async def get_messages():
    try:
        with db:
            db.create_tables([Messages, AIResponseCache], safe=True)
            results = (Messages
                       .select(
                           Messages.id,
                           Messages.sender_id,
                           Messages.receiver_id,
                           Messages.content,
                           Messages.sent_at,
                           AIResponseCache.id.alias('ai_response_id'),
                           AIResponseCache.message_id,
                           AIResponseCache.ai_response,
                           AIResponseCache.generated_at
                       )
                       .join(AIResponseCache, JOIN.LEFT_OUTER, on=(Messages.id == AIResponseCache.message_id))
                       .dicts())
            # Transform results to nest ai_response
            formatted_results = []
            for row in results:
                formatted_row = {
                    'id': row['id'],
                    'sender_id': row['sender_id'],
                    'receiver_id': row['receiver_id'],
                    'content': row['content'],
                    'sent_at': row['sent_at'].strftime('%Y-%m-%dT%H:%M:%S'),
                    'ai_response': {
                        'id': row['ai_response_id'],
                        'message_id': row['message_id'],
                        'ai_response': row['ai_response'],
                        'generated_at': row['generated_at'].strftime('%Y-%m-%dT%H:%M:%S') if row['generated_at'] else None
                    } if row['ai_response_id'] else None
                }
                formatted_results.append(formatted_row)
            return formatted_results
    except Exception as e:
        return {"error": str(e)}

@app.get("/test")
async def test():
    return {"status": "Backend is running"}
