# hosts

## GET `/api/hosts`

- Retrieve a list of hosts created by the authenticated user, with optional filtering by frequency.
- Operation ID: `hostapi_list_hosts_faeebded`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| address | query | no | string \| null |  |  |
| host_type | query | no | string \| null |  |  |
| month | query | no | integer \| null |  |  |
| duration | query | no | string \| null |  |  |
| ordering | query | no | string \| null |  | default=created_at |
| search | query | no | string \| null |  |  |
| page | query | no | integer |  | minimum=1; default=1 |
| page_size | query | no | integer \| null |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: NinjaPaginationResponseSchema_HostResponseSchema_ |

## POST `/api/hosts`

- Create a new host entry.
- Operation ID: `hostapi_create_host_0e257544`
- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `HostCreateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: HostResponseSchema |

## DELETE `/api/hosts/{host_id}`

- Delete a host entry.
- Operation ID: `hostapi_delete_host_8105934e`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| host_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## PATCH `/api/hosts/{host_id}`

- Update an existing host entry.
- Operation ID: `hostapi_update_host_df33b3a3`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| host_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `HostUpdateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: HostResponseSchema |

## GET `/api/hosts/{host_id}/vacancies`

- Retrieve a list of vacancies for a specific host.
- Operation ID: `hostapi_list_vacancies_b299a800`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| host_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: array[VacancyResponseSchema] |

## POST `/api/hosts/{host_id}/vacancies`

- Create a new vacancy for a host.
- Operation ID: `hostapi_create_vacancy_ef34dde9`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| host_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `VacancyCreateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 201 | Created | application/json: VacancyResponseSchema |

## DELETE `/api/hosts/vacancies/{vacancy_id}`

- Delete a vacancy.
- Operation ID: `hostapi_delete_vacancy_0d63dbce`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| vacancy_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## GET `/api/hosts/vacancies/{vacancy_id}`

- Retrieve details of a specific vacancy.
- Operation ID: `hostapi_get_vacancy_1aa2c00b`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| vacancy_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: VacancyResponseSchema |

## PATCH `/api/hosts/vacancies/{vacancy_id}`

- Update an existing vacancy.
- Operation ID: `hostapi_update_vacancy_285f6f57`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| vacancy_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `VacancyUpdateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: VacancyResponseSchema |