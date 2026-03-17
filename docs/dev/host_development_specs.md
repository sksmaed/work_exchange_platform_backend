# Host Module Development Specifications

## 1. Architecture Context
Connects to `core.User` through establishing `Host` profiles. `Vacancy` acts as a child to the `Host` model. Exposes operations via `HostControllerAPI`.

## 2. Data Models (Schema)

### 2.1. `Host`
Inherits from `BaseModel`.
- **References**: `user` (ForeignKey: `core.User`)
- **Metadata**: `name`, `type`, `address`, `phone_number`, `contact_information`, `description`
- **Offerings**: `pocket_money` (IntegerField), `meals_offered`, `dayoffs`, `facilities`, `other`
- **Expectations**: `expected_duration`, `expected_licenses` (later transformed: `vehicle` Choices), `expected_age`, `expected_gender`, `expected_personality`, `expected_other_requirements`
- **Branding**: `recruitment_slogan`, `host_image` (ImageField)
- **Feedback**: `avg_rating` (FloatField)

### 2.2. `Vacancy`
Inherits from `BaseModel`.
- **References**: `host` (ForeignKey: `host.Host`)
- **Metadata**: `name`, `work_time`, `description`
- **Expectations**: `expected_duration`, `expected_age`, `expected_gender`, `expected_licenses`, `expected_personality`, `expected_other_requirements`
- **Application Process**: `other_questions` (ArrayField of CharField)
- **Media**: `vacancy_image` (ImageField)
- **Status Management**: `status` (Choices: Recruiting, Full, Unavailable)

## 3. API Endpoints
- **`HostControllerAPI`** (registered in `config.api`): Exposes operations to view, create, and update Host profiles and their nested Vacancies.
