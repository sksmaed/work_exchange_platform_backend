# helper_resume

## POST `/api/helper/resume/`

- Create a new resume for the authenticated user.
- Operation ID: `helperresumeapi_create_resume_7fe79794`
- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `ResumeCreate` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 201 | Created | application/json: ResumeOut |

## PUT `/api/helper/resume/`

- Update the authenticated user's resume.
- Operation ID: `helperresumeapi_update_resume_18438832`
- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `ResumeUpdate` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: ResumeOut |

## GET `/api/helper/resume/self/`

- Retrieve the authenticated user's resume.
- Operation ID: `helperresumeapi_get_self_resume_7f2a569b`
- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: ResumeOut |