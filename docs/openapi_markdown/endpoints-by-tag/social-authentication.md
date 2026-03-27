# Social Authentication

## POST `/api/social-auth/apple/`

- Apple Sign In OAuth2 Login. Exchange Apple identity token (id_token) for JWT tokens. Args: request: The HTTP request object data: Apple login data containing id_token Returns: JWT tokens and user information
- Operation ID: `socialauth_apple_login_b528c37d`
- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `AppleLoginRequestSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## POST `/api/social-auth/facebook/`

- Facebook OAuth2 Login. Exchange Facebook access token for JWT tokens. Args: request: The HTTP request object data: Facebook login data containing access_token Returns: JWT tokens and user information
- Operation ID: `socialauth_facebook_login_54380561`
- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `FacebookLoginRequestSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## POST `/api/social-auth/google/`

- Google OAuth2 Login. Exchange Google access token for JWT tokens. Args: request: The HTTP request object data: Google login data containing access_token Returns: JWT tokens and user information
- Operation ID: `socialauth_google_login_1c75de17`
- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `GoogleLoginRequestSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |