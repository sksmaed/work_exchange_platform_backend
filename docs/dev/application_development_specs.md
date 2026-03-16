# Application Module Development Specifications

## 1. Architecture Context
An intermediary module establishing functional connections between `Vacancy` (from `host`) and `HelperModel` (from `helper`). Operates heavily using endpoints in `application.apis`.

## 2. Controllers & API Schema
- **Application Controller**: Exposes endpoints allowing Helpers to apply, and Hosts to update statuses.
- Exposes permission layers overriding base logic, strictly checking if `request.user == Application.vacancy.host.user`.
- Validations ensure proper data schemas are fulfilled during submission and status transformation.

## 3. Integrations
- **Calendar API**: Triggers a webhook or an internal service call to instantiate an event in the Calendar feature when an application status changes to "Accepted".
