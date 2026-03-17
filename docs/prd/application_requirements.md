# Application Module Requirements

## 1. Overview
The Application Module bridges Helpers and Hosts, allowing helpers to apply to vacancies, and hosts to review, accept, or reject those applications. It also syncs accepted applications with calendar events for scheduling.

## 2. Key Functional Requirements

### 2.1. Submission and Processing
- Helpers can submit applications for specific Vacancies.
- Hosts can review applications submitted to their vacancies and update the application status (e.g., Pending, Accepted, Rejected).
- Ensure authorization rules allow only the owner (the Host) of a Vacancy to alter the application status.

### 2.2. Calendar Sync
- When a Host updates an application status to "Accepted", the system must automatically create a corresponding Calendar Event to reflect the schedule.
- Calendar events must be capable of being updated, listed, and deleted.
