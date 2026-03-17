# Forum Module Development Specifications

## 1. Architecture Context
An independent module enabling social interactions globally across the app. Ties natively to `core.User` while tracking its own contextual hierarchy (Category -> Thread -> Reply).

## 2. Data Models (Schema)

### 2.1. `ForumCategory`
Inherits from `BaseModel`.
- **Metadata**: `name`, `description`, `order` (IntegerField)
- **Handling**: Sorted primarily ascending via `order`, then `name`.

### 2.2. `ForumThread`
Inherits from `BaseModel`.
- **References**: `author` (ForeignKey: `core.User`), `category` (ForeignKey: `forum.ForumCategory`, nullable)
- **Metadata**: `title`, `content`
- **Indices**: Indexed securely on `category`, `author`, and `-created_at`.

### 2.3. `ForumThreadImage`
Inherits from `BaseModel`.
- **References**: `thread` (ForeignKey: `forum.ForumThread`)
- **Media**: `image` (ImageField)

### 2.4. `ForumReply`
Inherits from `BaseModel`.
- **References**: `thread` (ForeignKey: `forum.ForumThread`), `author` (ForeignKey: `core.User`)
- **Metadata**: `content`
- **Indices**: Ordered natively by `created_at`. Indexed heavily on `thread`, `created_at`, and `author`.

### 2.5. `ForumReplyImage`
Inherits from `BaseModel`.
- **References**: `reply` (ForeignKey: `forum.ForumReply`)
- **Media**: `image` (ImageField)

## 3. API Endpoints
- **`ForumControllerAPI`** (registered in `config.api`): Exposes broad operations allowing Thread creation, Reply insertion, image uploads, and timeline viewing.
