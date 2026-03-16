# Helper Module Development Specifications

## 1. Architecture Context
This module establishes a one-to-one relationship with the `core.User` model for helpers. It encompasses `HelperModel`, `HelperPhoto`, and `HelperResume`.

## 2. Data Models (Schema)

### 2.1. `HelperModel`
Inherits from `BaseModel`.
- `user`: ForeignKey to `core.User`
- `description`, `birthday`, `gender` (Choices: M/F), `residence`
- JSON fields for flexible arrays: `expected_place`, `expected_time_periods`, `expected_treatments`, `languages`
- Text fields: `personality`, `motivation`, `hobbies`
- `licenses` (Choices: None, Driving, Motorcycle, Both)
- `avg_rating`: FloatField

### 2.2. `HelperPhoto`
Inherits from `BaseModel`.
- `helper`: ForeignKey to `HelperModel` (related_name="photos")
- `image`: ImageField
- `alt_text`: CharField
- `order`: PositiveIntegerField (controls display order)

### 2.3. `HelperResume`
Inherits from `BaseModel`.
- `helper`: OneToOneField to `HelperModel` (related_name="resume")
- `title`, `summary`
- JSON/Array fields: `experiences`, `certifications`, `availability`, `preferred_locations`, `skills` (ArrayField)
- Contact Info: `contact_email`, `contact_phone`

## 3. API Endpoints
- **`HelperResumeAPI`** (registered in `config.api`): Exposes operations to view, create, and update resumes. (Handled via controllers).
