from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.services.conversations.message_buffer import buffer_message
from app.db.session import get_db
from app.api.v1.billing import router as billing_router


app = FastAPI()

app.include_router(billing_router, prefix="/api/v1/billing")

@app.get('/health')
async def health_check():
    return {'status': 'ok', 'service': 'whatsapp-ai-bot'}

@app.get('/health/db')
async def health_db(db: Session = Depends(get_db)):
    try:
        # Testa conexão com PostgreSQL
        result = db.execute(text("SELECT 1"))
        return {
            'status': 'ok',
            'database': 'connected',
            'test_query': result.scalar()
        }
    except Exception as e:
        return {
            'status': 'error',
            'database': 'disconnected',
            'error': str(e)
        }

@app.post('/webhook')
async def webhook(request: Request):
    data = await request.json()
    chat_id = data.get('data').get('key').get('remoteJid')
    message = data.get('data').get('message').get('conversation')

    if chat_id and message and not '@g.us' in chat_id:
        await buffer_message(
            chat_id=chat_id,
            message=message,
        )

    return {'status': 'ok'}
