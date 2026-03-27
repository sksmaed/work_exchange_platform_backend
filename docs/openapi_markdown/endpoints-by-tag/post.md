# post

## GET `/api/hosts/{host_id}/posts`

- List posts for a host.
- Operation ID: `hostpostapi_list_posts_e8ba2be0`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| host_id | path | yes | string |  |  |
| page | query | no | integer |  | default=1 |
| page_size | query | no | integer |  | default=20 |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: PostListResponseSchema |

## POST `/api/hosts/{host_id}/posts`

- Create a post for the host.
- Operation ID: `hostpostapi_create_post_97aba662`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| host_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `multipart/form-data` | `object` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## DELETE `/api/posts/{post_id}`

- Delete a post.
- Operation ID: `postactionapi_delete_post_f1cb748e`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| post_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## GET `/api/posts/{post_id}`

- Get a post by ID.
- Operation ID: `postactionapi_get_post_80813f16`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| post_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## PATCH `/api/posts/{post_id}`

- Update a post's content.
- Operation ID: `postactionapi_update_post_2777b30a`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| post_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `PostUpdateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## GET `/api/posts/{post_id}/comments`

- List comments for a post.
- Operation ID: `postactionapi_list_comments_f8ad7a4b`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| post_id | path | yes | string |  |  |
| page | query | no | integer |  | default=1 |
| page_size | query | no | integer |  | default=20 |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: CommentListResponseSchema |

## POST `/api/posts/{post_id}/comments`

- Create a comment on a post.
- Operation ID: `postactionapi_create_comment_3fa35c03`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| post_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/x-www-form-urlencoded` | `object` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## DELETE `/api/posts/{post_id}/comments/{comment_id}`

- Delete a comment from a post.
- Operation ID: `postactionapi_delete_comment_5985c52f`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| post_id | path | yes | string |  |  |
| comment_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## POST `/api/posts/{post_id}/likes`

- Toggle like status on a post.
- Operation ID: `postactionapi_toggle_like_7d659e72`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| post_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |