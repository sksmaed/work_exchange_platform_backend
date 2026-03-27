# Schemas

## AlbumPhotoResponseSchema
Schema for a single album photo.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string | yes |  |  |
| image_url | string | yes |  |  |
| order | integer | yes |  |  |
| created_at | string (date-time) | yes |  |  |

## AlbumPhotoUploadResponseSchema
Schema for the response after uploading photos.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| image_urls | array[string] | yes |  |  |

## AlbumResponseSchema
Schema for a host's full album (paginated).

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| host_id | string | yes |  |  |
| photos | array[AlbumPhotoResponseSchema] | yes |  |  |
| total | integer | yes |  |  |
| page | integer | yes |  |  |
| page_size | integer | yes |  |  |
| has_next | boolean | yes |  |  |

## AppleLoginRequestSchema
Schema for Apple login request.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id_token | string | yes |  |  |

## ApplicationCreateSchema
Schema for creating an application.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| vacancy_id | string | yes |  |  |
| start_date | string (date) | yes |  |  |
| end_date | string (date) | yes |  |  |

## ApplicationResponseSchema
Schema for Application response.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string (uuid) | yes |  |  |
| helper | HelperProfileResponseSchema \| object \| null | no |  |  |
| vacancy | VacancyResponseSchema \| object \| null | no |  |  |
| status | string | no |  | maxLength=20; default=pending |
| start_date | string (date) | yes |  |  |
| end_date | string (date) | yes |  |  |

## ApplicationStatusUpdateSchema
Schema for updating an application's status.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| status | string | yes |  |  |

## CalendarEventResponseSchema
Schema for CalendarEvent response.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string (uuid) | yes |  |  |
| helper | HelperProfileResponseSchema \| null | no |  |  |
| host | string (uuid) | yes |  |  |
| application | string (uuid) \| null | no |  |  |
| start_date | string (date) | yes |  |  |
| end_date | string (date) | yes |  |  |
| remarks | string \| null | no |  | default= |

## CalendarEventUpdateSchema
Schema for updating a calendar event.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| start_date | string (date) \| null | no |  |  |
| end_date | string (date) \| null | no |  |  |
| remarks | string \| null | no |  |  |

## CommentListResponseSchema
Comment list response schema.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| post_id | string (uuid) | yes |  |  |
| comments | array[CommentResponseSchema] | yes |  |  |
| total | integer | yes |  |  |
| page | integer | yes |  |  |
| page_size | integer | yes |  |  |
| has_next | boolean | yes |  |  |

## CommentResponseSchema
Comment response schema.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string (uuid) | yes |  |  |
| post_id | string (uuid) | yes |  |  |
| user | UserSimpleResponseSchema | yes |  |  |
| content | string | yes |  |  |
| created_at | string (date-time) | yes |  |  |

## ConversationCreateSchema
Schema for creating or getting a conversation.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| participant_id | string (uuid) | yes |  |  |

## ConversationResponseSchema
Schema for conversation response.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string | yes |  |  |
| participant_1 | UserBasicSchema | yes |  |  |
| participant_2 | UserBasicSchema | yes |  |  |
| last_message_at | string (date-time) \| null | yes |  |  |
| created_at | string (date-time) | yes |  |  |
| unread_count | integer | no |  | default=0 |

## DynamicInput

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| ordering | string \| null | no |  | default=created_at |

## FacebookLoginRequestSchema
Schema for Facebook login request.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| access_token | string | yes |  |  |

## ForumCategoryResponseSchema
Schema for forum category response.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string | yes |  |  |
| name | string | yes |  |  |
| description | string | yes |  |  |
| order | integer | yes |  |  |
| created_at | string (date-time) | yes |  |  |

## ForumImageUploadResponseSchema
Schema for image upload response.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| image_urls | array[string] | yes |  |  |

## ForumReplyCreateSchema
Schema for creating a forum reply.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| content | string | yes |  |  |

## ForumReplyResponseSchema
Schema for forum reply response.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string | yes |  |  |
| thread_id | string | yes |  |  |
| author | UserBasicSchema | yes |  |  |
| content | string | yes |  |  |
| image_urls | array[string] | no |  | default= |
| created_at | string (date-time) | yes |  |  |

## ForumReplyUpdateSchema
Schema for updating a forum reply.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| content | string | yes |  |  |

## ForumThreadCreateSchema
Schema for creating a forum thread.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| title | string | yes |  | maxLength=255 |
| content | string | yes |  |  |
| category_id | string \| null | no |  |  |

## ForumThreadDetailResponseSchema
Schema for thread detail with replies.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string | yes |  |  |
| title | string | yes |  |  |
| content | string | yes |  |  |
| author | UserBasicSchema | yes |  |  |
| category_id | string \| null | yes |  |  |
| category_name | string \| null | yes |  |  |
| reply_count | integer | yes |  |  |
| image_urls | array[string] | no |  | default= |
| replies | array[ForumReplyResponseSchema] | yes |  |  |
| created_at | string (date-time) | yes |  |  |

## ForumThreadListPaginatedSchema
Schema for paginated thread list.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| items | array[ForumThreadListResponseSchema] | yes |  |  |
| total | integer | yes |  |  |
| page | integer | yes |  |  |
| page_size | integer | yes |  |  |
| has_next | boolean | yes |  |  |

## ForumThreadListResponseSchema
Schema for thread in list view.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string | yes |  |  |
| title | string | yes |  |  |
| content | string | yes |  |  |
| author | UserBasicSchema | yes |  |  |
| category_id | string \| null | yes |  |  |
| category_name | string \| null | yes |  |  |
| reply_count | integer | yes |  |  |
| image_urls | array[string] | no |  | default= |
| created_at | string (date-time) | yes |  |  |

## ForumThreadUpdateSchema
Schema for updating a forum thread.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| title | string \| null | no |  |  |
| content | string \| null | no |  |  |
| category_id | string \| null | no |  |  |

## GoogleLoginRequestSchema
Schema for Google login request.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| access_token | string | yes |  |  |

## HelperProfileCreateSchema
Schema for creating a helper profile.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| description | string | yes |  |  |
| birthday | string (date) | yes |  |  |
| gender | string | yes |  |  |
| residence | string \| null | no |  | default= |
| expected_place | array[string] \| null | no |  |  |
| expected_time_periods | array[TimePeriodSchema] \| null | no |  |  |
| expected_treatments | array[string] \| null | no |  |  |
| personality | string \| null | no |  | default= |
| motivation | string \| null | no |  | default= |
| hobbies | string \| null | no |  | default= |
| licenses | string \| null | no |  | default=None |
| languages | array[string] \| null | no |  |  |

## HelperProfileResponseSchema
Schema for the helper profile response.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string (uuid) | yes |  |  |
| description | string | yes |  |  |
| birthday | string (date) | yes |  |  |
| gender | string | yes |  |  |
| residence | string | yes |  |  |
| expected_place | array[string] | yes |  |  |
| expected_time_periods | array[object] | yes |  |  |
| expected_treatments | array[string] | yes |  |  |
| personality | string | yes |  |  |
| motivation | string | yes |  |  |
| hobbies | string | yes |  |  |
| licenses | string | yes |  |  |
| languages | array[string] | yes |  |  |
| avg_rating | number | yes |  |  |

## HelperProfileUpdateSchema
Schema for updating a helper profile.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| description | string \| null | no |  |  |
| birthday | string (date) \| null | no |  |  |
| gender | string \| null | no |  |  |
| residence | string \| null | no |  |  |
| expected_place | array[string] \| null | no |  |  |
| expected_time_periods | array[TimePeriodSchema] \| null | no |  |  |
| expected_treatments | array[string] \| null | no |  |  |
| personality | string \| null | no |  |  |
| motivation | string \| null | no |  |  |
| hobbies | string \| null | no |  |  |
| licenses | string \| null | no |  |  |
| languages | array[string] \| null | no |  |  |

## HostCreateSchema
Schema for creating a new Host.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| description | string | yes |  |  |
| address | string | yes |  |  |
| type | string | yes |  |  |
| contact_information | string \| null | no |  | default= |
| pocket_money | integer \| null | no |  | default=0 |
| meals_offered | string \| null | no |  | default= |
| dayoffs | string \| null | no |  | default= |
| allowance | string \| null | no |  | default= |
| facilities | string \| null | no |  | default= |
| other | string \| null | no |  | default= |
| expected_duration | string \| null | no |  | default= |
| recruitment_slogan | string \| null | no |  | default= |

## HostResponseSchema
Schema for Host response.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| exclude_children | boolean \| null | no |  |  |
| months | array[integer] | no |  |  |
| duration_options | array[string] | no |  |  |
| keywords | array[string] | no |  |  |
| id | string (uuid) \| null | no |  |  |
| created_at | string (date-time) | yes |  |  |
| created_by_user | string (uuid) \| null | no |  |  |
| user | string (uuid) | yes |  |  |
| name | string | yes |  | maxLength=100 |
| address | string | no |  | maxLength=100; default= |
| type | string | yes |  | maxLength=50 |
| phone_number | string | yes |  | maxLength=15 |
| contact_information | string \| null | no |  | default= |
| description | string | yes |  |  |
| pocket_money | integer | no |  | default=0 |
| meals_offered | string \| null | no |  | default= |
| dayoffs | string \| null | no |  | default= |
| facilities | string \| null | no |  | default= |
| other | string \| null | no |  | default= |
| expected_duration | string \| null | no |  | default= |
| vehicle | string | no |  | maxLength=20; default=None |
| recruitment_slogan | string \| null | no |  | default= |
| host_image | string \| null | no |  |  |
| avg_rating | number \| null | no |  | default=0 |

## HostUpdateSchema
Schema for updating Host.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| description | string \| null | no |  |  |
| type | string \| null | no |  |  |
| address | string \| null | no |  |  |
| contact_information | string \| null | no |  |  |
| pocket_money | integer \| null | no |  |  |
| meals_offered | string \| null | no |  |  |
| dayoffs | string \| null | no |  |  |
| allowance | string \| null | no |  |  |
| facilities | string \| null | no |  |  |
| other | string \| null | no |  |  |
| expected_duration | string \| null | no |  |  |
| recruitment_slogan | string \| null | no |  |  |

## MarkAsReadSchema
Schema for marking messages as read.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| message_ids | array[string] \| null | no |  |  |

## MessageCreateSchema
Schema for creating a new message.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| content | string | yes |  | minLength=1; maxLength=5000 |

## MessageListResponseSchema
Schema for paginated message list response.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| messages | array[MessageResponseSchema] | yes |  |  |
| total | integer | yes |  |  |
| page | integer | yes |  |  |
| page_size | integer | yes |  |  |
| has_next | boolean | yes |  |  |

## MessageResponseSchema
Schema for message response.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string | yes |  |  |
| conversation_id | string | yes |  |  |
| sender | UserBasicSchema | yes |  |  |
| content | string | yes |  |  |
| read_at | string (date-time) \| null | yes |  |  |
| created_at | string (date-time) | yes |  |  |

## ninja__pagination__PageNumberPagination__Input

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| page | integer | no |  | minimum=1; default=1 |
| page_size | integer \| null | no |  |  |

## ninja_extra__searching__models__Searching__Input

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| search | string \| null | no |  |  |

## NinjaPaginationResponseSchema_HostResponseSchema_

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| count | integer | yes |  |  |
| items | array[HostResponseSchema] | yes |  |  |

## NinjaPaginationResponseSchema_VacancyResponseSchema_

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| count | integer | yes |  |  |
| items | array[VacancyResponseSchema] | yes |  |  |

## PostLikeResponseSchema
Post like response schema.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| post_id | string (uuid) | yes |  |  |
| like_count | integer | yes |  |  |
| liked | boolean | yes |  |  |

## PostListResponseSchema
Post list response schema.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| host_id | string (uuid) | yes |  |  |
| posts | array[PostResponseSchema] | yes |  |  |
| total | integer | yes |  |  |
| page | integer | yes |  |  |
| page_size | integer | yes |  |  |
| has_next | boolean | yes |  |  |

## PostPhotoResponseSchema
Post photo response schema.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string (uuid) | yes |  |  |
| image_url | string | yes |  |  |
| order | integer | yes |  |  |

## PostResponseSchema
Post response schema.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string (uuid) | yes |  |  |
| host_id | string (uuid) | yes |  |  |
| content | string | yes |  |  |
| like_count | integer | yes |  |  |
| comment_count | integer | yes |  |  |
| photos | array[PostPhotoResponseSchema] | yes |  |  |
| is_liked_by_me | boolean | no |  | default=false |
| created_at | string (date-time) | yes |  |  |
| updated_at | string (date-time) | yes |  |  |

## PostUpdateSchema
Post update schema.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| content | string | yes |  |  |

## ResumeCreate

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| title | string \| null | no |  |  |
| summary | string \| null | no |  |  |
| experiences | array[object] \| null | no |  |  |
| skills | array[string] \| null | no |  |  |
| certifications | array[string] \| null | no |  |  |
| availability | array[object] \| null | no |  |  |
| preferred_locations | array[string] \| null | no |  |  |
| contact_email | string \| null | no |  |  |
| contact_phone | string \| null | no |  |  |

## ResumeOut

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| title | string \| null | no |  |  |
| summary | string \| null | no |  |  |
| experiences | array[object] \| null | no |  |  |
| skills | array[string] \| null | no |  |  |
| certifications | array[string] \| null | no |  |  |
| availability | array[object] \| null | no |  |  |
| preferred_locations | array[string] \| null | no |  |  |
| contact_email | string \| null | no |  |  |
| contact_phone | string \| null | no |  |  |
| id | string | yes |  |  |

## ResumeUpdate

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| title | string \| null | no |  |  |
| summary | string \| null | no |  |  |
| experiences | array[object] \| null | no |  |  |
| skills | array[string] \| null | no |  |  |
| certifications | array[string] \| null | no |  |  |
| availability | array[object] \| null | no |  |  |
| preferred_locations | array[string] \| null | no |  |  |
| contact_email | string \| null | no |  |  |
| contact_phone | string \| null | no |  |  |

## TimePeriodSchema
Schema representing a generic time period.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| start_date | string (date) | yes |  |  |
| end_date | string (date) | yes |  |  |

## UserBasicSchema
Basic user information schema.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string | yes |  |  |
| name | string | yes |  |  |
| email | string | yes |  |  |
| avatar | string \| null | no |  |  |

## UserSimpleResponseSchema
User simple response schema.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| id | string (uuid) | yes |  |  |
| username | string | yes |  |  |
| email | string | yes |  |  |

## VacancyAvailabilitySchema
Schema for Vacancy availability.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| start_date | string (date) | yes |  |  |
| end_date | string (date) | yes |  |  |
| capacity | integer | no |  | default=1 |
| current_helpers | integer | no |  | default=0 |

## VacancyCreateSchema
Schema for creating a new Vacancy.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| host_id | string | yes |  |  |
| name | string | yes |  |  |
| work_time | string | yes |  |  |
| description | string | yes |  |  |
| expected_duration | string | yes |  |  |
| expected_age | string | yes |  |  |
| expected_gender | string | yes |  |  |
| expected_licenses | string | yes |  |  |
| expected_personality | string | yes |  |  |
| expected_other_requirements | string | yes |  |  |
| other_questions | array[string] | no |  |  |
| status | string | no |  | default=Recruiting |
| availabilities | array[object] | no |  |  |

## VacancyResponseSchema
Schema for Vacancy response.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| availabilities | array[VacancyAvailabilitySchema] | no |  |  |
| id | string (uuid) \| null | no |  |  |
| created_at | string (date-time) | yes |  |  |
| created_by_user | string (uuid) \| null | no |  |  |
| host | string (uuid) | yes |  |  |
| name | string | yes |  | maxLength=100 |
| work_time | string | yes |  | maxLength=100 |
| description | string | yes |  |  |
| expected_duration | string | yes |  | maxLength=100 |
| expected_age | string | yes |  | maxLength=100 |
| expected_gender | string | yes |  | maxLength=100 |
| expected_licenses | string | yes |  | maxLength=100 |
| expected_personality | string | yes |  |  |
| expected_other_requirements | string | yes |  |  |
| other_questions | array[object] \| null | no |  |  |
| vacancy_image | string \| null | no |  |  |
| status | string | no |  | maxLength=20; default=Recruiting |

## VacancyUpdateSchema
Schema for updating a Vacancy.

| Property | Type | Required | Description | Constraints |
| --- | --- | --- | --- | --- |
| name | string \| null | no |  |  |
| work_time | string \| null | no |  |  |
| description | string \| null | no |  |  |
| expected_duration | string \| null | no |  |  |
| expected_age | string \| null | no |  |  |
| expected_gender | string \| null | no |  |  |
| expected_licenses | string \| null | no |  |  |
| expected_personality | string \| null | no |  |  |
| expected_other_requirements | string \| null | no |  |  |
| other_questions | array[string] \| null | no |  |  |
| status | string \| null | no |  |  |
| availabilities | array[object] \| null | no |  |  |
