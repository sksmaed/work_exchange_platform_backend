# Backend Architecture Overview

## Introduction
The Work Exchange Platform backend is built using Django and the Django Ninja Extra API framework. It provides a RESTful API architecture to manage interactions between "Hosts" (who offer work/exchange opportunities) and "Helpers" (who apply for these opportunities), along with community features like chat and forums.

## Core Technologies
*   **Framework**: Django
*   **API Framework**: Django Ninja Extra / Ninja
*   **Database**: PostgreSQL (indicated by `ArrayField` and `JSONField` usage)
*   **Authentication**: Custom User model, Social Authentication
*   **Tooling**: Ruff, Pre-commit
*   **Containerization**: Docker & Docker Compose (`docker-compose.yml`, `Dockerfile`)

## Module Architecture (Features)
The applications are structured under the `features/` directory to enforce domain-driven design. The main modules are:

1.  **Core (`features/core`)**: Handles base user accounts, distinguishing between 'helper', 'host', or 'both'. Handles system-wide utilities and social authentication.
2.  **Helper (`features/helper`)**: Manages the helper profiles, including attributes like skills, languages, expected treatments, and helper resumes.
3.  **Host (`features/host`)**: Manages host profiles (locations, offered meals, allowances) and their associated `Vacancy` postings (work time, conditions, expected licenses, etc.).
4.  **Application (`features/application`)**: Manages the workflows of helpers applying for specific vacancies offered by hosts.
5.  **Chat (`features/chat`)**: Provides 1-on-1 private messaging functionality between users with read receipt tracking.
6.  **Forum (`features/forum`)**: Provides a community discussion board structured with categories, threads, and replies, including image attachments.

## Project Structure
*   `common/`: Shared models (e.g., `BaseModel` handles `created_at` and `updated_at`), exceptions, and managers.
*   `config/`: Main Django settings and main API router entry point (`api.py`).
*   `features/`: Domain-specific business logic and models.
*   `utils/`: Helper utilities (e.g., file storage implementations).

## Data Flow
Clients (frontend/mobile) interact via JSON over HTTP to the endpoints exposed by Django Ninja. The API endpoints resolve the requests using domain controllers/services which read and write to the PostgreSQL database via Django ORM.

## Error Handling
A unified error handling loop is configured in `config/api.py` to capture `BaseAPIException` and present uniform JSON response structures to the frontend.
