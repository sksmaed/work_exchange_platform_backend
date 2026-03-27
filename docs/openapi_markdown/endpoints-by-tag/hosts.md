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

**Response Example**
```json
{
  "count": 2,
  "items": [
    {
      "exclude_children": false,
      "months": [3, 4, 5],
      "duration_options": ["2 weeks", "1 month"],
      "keywords": ["breakfast", "lunch"],
      "id": "0f3a2b28-0b0e-4b6b-8b7a-7a3c2f8f2a10",
      "created_at": "2026-03-27T09:15:30Z",
      "created_by_user": "7d59a4e8-2b2a-4c1a-8c0c-3c8d5f7b2a01",
      "user": "7d59a4e8-2b2a-4c1a-8c0c-3c8d5f7b2a01",
      "name": "Sunny Farm",
      "address": "Hsinchu",
      "type": "farm",
      "phone_number": "0912345678",
      "contact_information": "Line: sunnyfarm",
      "description": "Organic farm work exchange.",
      "pocket_money": 0,
      "meals_offered": "breakfast, lunch",
      "dayoffs": "Sun",
      "facilities": "WiFi",
      "other": "",
      "expected_duration": "1 month",
      "vehicle": "None",
      "recruitment_slogan": "Join us!",
      "host_image": null,
      "avg_rating": 4.6
    }
  ]
}
```

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
