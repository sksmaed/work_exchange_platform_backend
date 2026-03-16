# Helper Module Requirements

## 1. Overview
The Helper Module tracks the profiles, resumes, and specific details of users who intend to apply for work exchange vacancies.

## 2. Key Functional Requirements

### 2.1. Helper Profile Management
- Helpers must define personal details such as description, birthday, gender, and residence.
- Helpers must outline their preferences: Expected places, expected time periods, and expected treatments (pocket money, meals, etc.).
- Helpers must articulate soft traits like personality, motivation, and hobbies.
- Helpers should be able to tag licenses (e.g., Driving, Motorcycle) and languages spoken.
- The system must support uploading multiple helper photos for their portfolio/gallery, ordered by preference.

### 2.2. Helper Resume
- Helpers can create a structured resume detailing a `title` and `summary`.
- The resume should track `experiences`, `skills`, and `certifications` using JSON or Array structures.
- The resume must hold availability and preferred location settings independently.
- Include alternative contact methods (email, phone) in the resume.

### 2.3. Ratings
- Calculate and store a read-only or derived average rating (`avg_rating`) to reflect community feedback on the helper.
