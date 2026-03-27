# forum

## GET `/api/forum/categories`

- List all forum categories (public).
- Operation ID: `forumapi_list_categories_64b3c993`
- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: array[ForumCategoryResponseSchema] |

## DELETE `/api/forum/replies/{reply_id}`

- Delete a reply (author only).
- Operation ID: `forumapi_delete_reply_acabaaa7`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| reply_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## PATCH `/api/forum/replies/{reply_id}`

- Update a reply (author only).
- Operation ID: `forumapi_update_reply_dd424b39`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| reply_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `ForumReplyUpdateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: ForumReplyResponseSchema |

## POST `/api/forum/replies/{reply_id}/images`

- Add images to a reply (author only).
- Operation ID: `forumapi_add_reply_images_a0dd46c6`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| reply_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `multipart/form-data` | `object` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 201 | Created | application/json: ForumImageUploadResponseSchema |

## DELETE `/api/forum/replies/{reply_id}/images/{image_id}`

- Remove an image from a reply (author only).
- Operation ID: `forumapi_delete_reply_image_a4156e27`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| reply_id | path | yes | string |  |  |
| image_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## GET `/api/forum/threads`

- List forum threads with pagination (public).
- Operation ID: `forumapi_list_threads_d1bfb3bc`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| page | query | no | integer |  | default=1 |
| page_size | query | no | integer |  | default=20 |
| category_id | query | no | string \| null |  |  |
| search | query | no | string \| null |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: ForumThreadListPaginatedSchema |

## POST `/api/forum/threads`

- Create a new forum thread.
- Operation ID: `forumapi_create_thread_84d7be30`
- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `ForumThreadCreateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 201 | Created | application/json: ForumThreadDetailResponseSchema |

## DELETE `/api/forum/threads/{thread_id}`

- Delete a forum thread (author only).
- Operation ID: `forumapi_delete_thread_1e1fa8a0`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| thread_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## GET `/api/forum/threads/{thread_id}`

- Get a thread with its replies (public).
- Operation ID: `forumapi_get_thread_068efcd9`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| thread_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: ForumThreadDetailResponseSchema |

## PATCH `/api/forum/threads/{thread_id}`

- Update a forum thread (author only).
- Operation ID: `forumapi_update_thread_11b6d43e`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| thread_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `ForumThreadUpdateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: ForumThreadDetailResponseSchema |

## POST `/api/forum/threads/{thread_id}/images`

- Add images to a thread (author only).
- Operation ID: `forumapi_add_thread_images_8c04c6aa`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| thread_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `multipart/form-data` | `object` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 201 | Created | application/json: ForumImageUploadResponseSchema |

## DELETE `/api/forum/threads/{thread_id}/images/{image_id}`

- Remove an image from a thread (author only).
- Operation ID: `forumapi_delete_thread_image_c55a8343`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| thread_id | path | yes | string |  |  |
| image_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## POST `/api/forum/threads/{thread_id}/replies`

- Create a reply to a thread.
- Operation ID: `forumapi_create_reply_f7308ded`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| thread_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `ForumReplyCreateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 201 | Created | application/json: ForumReplyResponseSchema |