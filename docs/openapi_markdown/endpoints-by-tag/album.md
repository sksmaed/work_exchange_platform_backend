# album

## GET `/api/hosts/{host_id}/album`

- Get all photos in a host's album (public). Returns a paginated list of photos belonging to the given host.
- Operation ID: `albumapi_get_album_2ecc0779`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| host_id | path | yes | string |  |  |
| page | query | no | integer |  | default=1 |
| page_size | query | no | integer |  | default=20 |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: AlbumResponseSchema |

## POST `/api/hosts/{host_id}/album/photos`

- Upload one or more photos to the host's album (host owner only).
- Operation ID: `albumapi_upload_photos_3690fdb2`
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
| 201 | Created | application/json: AlbumPhotoUploadResponseSchema |

## DELETE `/api/hosts/{host_id}/album/photos/{photo_id}`

- Delete a specific photo from the host's album (host owner only).
- Operation ID: `albumapi_delete_photo_cc548af6`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| host_id | path | yes | string |  |  |
| photo_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |