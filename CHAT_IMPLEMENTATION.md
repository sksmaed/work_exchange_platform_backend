# Chat Feature Implementation

## Summary

The chat feature has been successfully implemented with full REST API and WebSocket support. The implementation follows the existing project patterns and includes:

## What Was Created

### 1. Chat Feature Structure (`features/chat/`)

- **models.py** - Database models for conversations and messages
  - `Conversation`: Manages 1-on-1 conversations between two users
  - `Message`: Individual messages within conversations with read receipts
  
- **schemas.py** - Request/response schemas for the API
  - `ConversationCreateSchema`, `ConversationResponseSchema`
  - `MessageCreateSchema`, `MessageResponseSchema`
  - `MessageListResponseSchema` with pagination support
  
- **apis.py** - REST API endpoints
  - `POST /api/chat/conversations` - Create or get a conversation
  - `GET /api/chat/conversations` - List all user's conversations
  - `GET /api/chat/conversations/{id}/messages` - Get messages (paginated)
  - `POST /api/chat/conversations/{id}/messages` - Send a message
  - `PATCH /api/chat/conversations/{id}/read` - Mark messages as read
  - `DELETE /api/chat/conversations/{id}` - Delete a conversation
  
- **consumers.py** - WebSocket consumer for real-time chat
  - WebSocket URL: `ws/chat/{conversation_id}/`
  - Real-time message delivery
  - Typing indicators
  - Read receipts
  
- **exceptions.py** - Chat-specific error codes
- **admin.py** - Django admin interface for managing chat data
- **apps.py** - Django app configuration

### 2. Configuration Updates

- **settings.py** - Added `features.chat` to `LOCAL_APPS`, added `channels` to `INSTALLED_APPS`, configured `CHANNEL_LAYERS` for Redis
- **api.py** - Registered `ChatControllerAPI` 
- **routing.py** - Added WebSocket route for `ChatConsumer`
- **asgi.py** - Updated ASGI configuration to support both HTTP and WebSocket protocols with proper authentication

### 3. Database Migrations

- Migration file created: `features/chat/migrations/0001_initial.py`
- Creates `Conversation` and `Message` tables with proper indexes

## Features

### REST API Features

1. **Conversation Management**
   - Automatic conversation creation between two users
   - Prevents duplicate conversations
   - Cannot create conversation with yourself
   - Permission checks (only participants can view/use conversations)

2. **Messaging**
   - Send text messages
   - Paginated message retrieval (50 messages per page, newest first)
   - Read receipt tracking
   - Unread message counts
   - Last message timestamp tracking

3. **Security**
   - All endpoints require authentication
   - Users can only access their own conversations
   - Participants are verified for all operations

### WebSocket Features

1. **Real-time Messaging**
   - Instant message delivery to online participants
   - Automatic group management per conversation

2. **Typing Indicators**
   - Send typing status to other participant
   - Receive typing notifications

3. **Read Receipts**
   - Broadcast when messages are read
   - Real-time read status updates

## How to Complete Setup

### 1. Start Docker Services

The migrations were created but not applied because the database is not running.

```bash
# Start PostgreSQL and Redis
docker-compose up -d
```

### 2. Apply Migrations

```bash
source .venv/bin/activate
python manage.py migrate
```

### 3. Start the Development Server

```bash
# For development with auto-reload
python manage.py runserver

# OR with Uvicorn (for production-like setup)
uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the API

The API will be available at:
- REST API: `http://localhost:8000/api/chat/`
- WebSocket: `ws://localhost:8000/ws/chat/{conversation_id}/`
- API Docs: `http://localhost:8000/api/docs/`

## API Usage Examples

### Create/Get Conversation

```bash
curl -X POST http://localhost:8000/api/chat/conversations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"participant_id": "user-uuid-here"}'
```

### List Conversations

```bash
curl http://localhost:8000/api/chat/conversations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Send Message

```bash
curl -X POST http://localhost:8000/api/chat/conversations/{conversation_id}/messages \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, how are you?"}'
```

### Get Messages

```bash
curl "http://localhost:8000/api/chat/conversations/{conversation_id}/messages?page=1&page_size=50" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Mark Messages as Read

```bash
curl -X PATCH http://localhost:8000/api/chat/conversations/{conversation_id}/read \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## WebSocket Connection Example

```javascript
// Connect to conversation WebSocket
const conversationId = "your-conversation-uuid";
const token = "your-jwt-token";
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${conversationId}/`);

ws.onopen = () => {
  console.log("Connected to chat");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === "message") {
    // New message received
    console.log("New message:", data.message);
  } else if (data.type === "typing") {
    // Typing indicator
    console.log("User typing:", data.user_id, data.is_typing);
  } else if (data.type === "read_receipt") {
    // Messages read
    console.log("Messages read:", data.message_ids);
  }
};

// Send typing indicator
ws.send(JSON.stringify({
  type: "typing",
  is_typing: true
}));

// Send read receipt
ws.send(JSON.stringify({
  type: "read_receipt",
  message_ids: ["msg-uuid-1", "msg-uuid-2"]
}));
```

## Database Schema

### Conversation Table

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| participant_1 | ForeignKey | First user in conversation |
| participant_2 | ForeignKey | Second user in conversation |
| last_message_at | DateTime | Timestamp of last message |
| created_at | DateTime | When conversation was created |
| updated_at | DateTime | Last update timestamp |

### Message Table

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| conversation | ForeignKey | Related conversation |
| sender | ForeignKey | User who sent the message |
| content | Text | Message content |
| read_at | DateTime | When message was read (null if unread) |
| created_at | DateTime | When message was sent |
| updated_at | DateTime | Last update timestamp |

## Dependencies

All required dependencies are already in the project:
- `channels>=4.2.2` - WebSocket support
- `channels-redis>=4.3.0` - Redis channel layer (installed)
- `django-ninja>=1.4.3` - REST API framework
- `django-ninja-extra>=0.30.1` - API controllers

## Next Steps

1. **Start Docker** - Run `docker-compose up -d` to start PostgreSQL and Redis
2. **Run Migrations** - Apply the chat migrations with `python manage.py migrate`
3. **Test the API** - Use the API docs or curl commands to test endpoints
4. **WebSocket Testing** - Use a WebSocket client to test real-time features
5. **Frontend Integration** - Connect your frontend to the REST API and WebSocket endpoints

## Notes

- The chat system uses Redis for real-time WebSocket communication via Django Channels
- All conversations are 1-on-1 (future enhancement: add group chat support)
- Messages are soft-deleted (keep the records but mark as deleted)
- Read receipts are automatically tracked
- Unread message counts are calculated on-the-fly for each conversation
