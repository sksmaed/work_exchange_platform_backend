# chat

## GET `/api/chat/conversations`

- List all conversations for the current user.
- Operation ID: `chatapi_list_conversations_e04d7239`
- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: array[ConversationResponseSchema] |

## POST `/api/chat/conversations`

- Create or get a conversation with another user.
- Operation ID: `chatapi_create_or_get_conversation_11ef0951`
- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `ConversationCreateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 201 | Created | application/json: ConversationResponseSchema |

## DELETE `/api/chat/conversations/{conversation_id}`

- Delete a conversation.
- Operation ID: `chatapi_delete_conversation_4c9e1adc`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| conversation_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## GET `/api/chat/conversations/{conversation_id}/messages`

- Get messages in a conversation with pagination.
- Operation ID: `chatapi_get_conversation_messages_2e6a91bd`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| conversation_id | path | yes | string |  |  |
| page | query | no | integer |  | default=1 |
| page_size | query | no | integer |  | default=50 |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: MessageListResponseSchema |

## POST `/api/chat/conversations/{conversation_id}/messages`

- Send a message in a conversation.
- Operation ID: `chatapi_send_message_4d87fa70`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| conversation_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `MessageCreateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 201 | Created | application/json: MessageResponseSchema |

## PATCH `/api/chat/conversations/{conversation_id}/read`

- Mark messages as read in a conversation.
- Operation ID: `chatapi_mark_messages_as_read_653daa87`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| conversation_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `MarkAsReadSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |