# Core Module Requirements

## 1. Overview
The Core Module handles the foundational aspects of the Work Exchange Platform, specifically concerning user authentication, authorization, and base user profiles. 

## 2. Target Audience
- Unregistered users (visitors)
- Registered Helpers
- Registered Hosts
- Dual-role Users (Both Helper and Host)

## 3. Key Functional Requirements

### 3.1. User Registration and Authentication
- Support standard Email/Password authentication.
- Support Social Authentication (e.g., Facebook Login, as indicated by `FACEBOOK_LOGIN_GUIDE.md`).
- Ensure email addresses and usernames are unique per account.

### 3.2. Role Management
- The system must distinguish between `helper`, `host`, or `both` user types, guiding them to their respective onboarding or dashboards.
- A single user account should be able to hold both roles if specified.

### 3.3. Profile Core Details
- Users must be able to specify `first_name`, `last_name`, and a general `name`.
- Users must be able to upload a profile avatar.
- The system should track the last login IP address.

## 4. Non-Functional Requirements
- High availability for the login service.
- Secure storage of credentials (handled natively by Django).
- Extensibility to allow future fields or third-party auth providers.
