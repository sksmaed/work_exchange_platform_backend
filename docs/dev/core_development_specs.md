# Core Module Development Specifications

## 1. Architecture Context
This module acts as the base for the application, interacting heavily with Django's native authentication framework. Other modules (Helper, Host, Chat, Forum) hold ForeignKeys referencing this module's `User` model.

## 2. Data Models (Schema)

### 2.1. `User` Model
Extends `django.contrib.auth.models.AbstractUser` and the project `BaseModel`.

**Fields:**
- `name` (CharField, max_length=255, blank=True)
- `first_name` (CharField, max_length=150, blank=True)
- `last_name` (CharField, max_length=150, blank=True)
- `username` (CharField, max_length=150, unique=True)
- `email` (EmailField, unique=True)
- `avatar` (ImageField, upload_to=get_model_file_path, null=True, blank=True)
- `last_login_ip` (GenericIPAddressField, protocol='IPv4', null=True, blank=True)
- `user_type` (CharField, choices=[helper, host, both], default=helper)

**Methods:**
- `get_full_name()`: Returns name or email.
- `get_short_name()`: Returns name or email.

## 3. API Endpoints (Controllers)
Handled via `api.py` in `features/core/api.py`.
- **`SocialAuthController`**: Handles third-party authentication logic, validating access tokens and setting up/linking user accounts.

## 4. Dependencies
- Django Auth
- `common.models.BaseModel`
- `utils.storage.get_model_file_path`
- Django Ninja API
