# Chat Module Development Specifications

## 1. Architecture Context
An essential connectivity tool mapping distinct users natively without relying on heavy third-party real-time SaaS. Leverages `core.User` extensively.

## 2. Data Models (Schema)

### 2.1. `Conversation`
Inherits from `BaseModel`.
- **References**: `participant_1` and `participant_2` (ForeignKeys: `core.User`)
- **Metadata**: `last_message_at` (DateTimeField)
- **Constraints**: 
  - Enforced Uniqueness: Participant 1 and Participant 2 must securely constitute a one-to-one conversation constraint, managed intrinsically via sorting (`id`) before instantiation.
- **Indices**: Ordered natively by `-last_message_at` and `-created_at`. Indexed heavily on participants and timestamps.
- **Methods**: `get_other_participant(user)`, `get_or_create_conversation(user1, user2)` (handles sorting logic internally).

### 2.2. `Message`
Inherits from `BaseModel`.
- **References**: `conversation` (ForeignKey: `chat.Conversation`), `sender` (ForeignKey: `core.User`)
- **Metadata**: `content` (TextField)
- **Tracking**: `read_at` (DateTimeField, nullable)
- **Indices**: Ordered natively by `created_at`. Indexed heavily on `conversation`, `created_at`, and `sender`.
- **Methods**: `mark_as_read()` updates `read_at` timestamp.

## 3. API Endpoints
- **`ChatControllerAPI`** (registered in `config.api`): Exposes conversational operations (e.g., retrieving history, sending messages, marking read).
