# helpers

## POST `/api/helpers/`

- Create a new helper profile for the authenticated user.
- Operation ID: `helperapi_create_helper_profile_40308ba0`
- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `HelperProfileCreateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 201 | Created | application/json: HelperProfileResponseSchema |

## GET `/api/helpers/self/`

- Retrieve the authenticated user's helper profile.
- Operation ID: `helperapi_get_self_profile_daa44c12`
- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: HelperProfileResponseSchema |

## PATCH `/api/helpers/self/`

- Update the authenticated user's helper profile.
- Operation ID: `helperapi_update_helper_profile_f1f9cd8f`
- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `HelperProfileUpdateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: HelperProfileResponseSchema |