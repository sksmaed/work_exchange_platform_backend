# vacancies

## GET `/api/vacancies/search`

- Search active vacancies with available capacity, optionally matching a specific date range.
- Operation ID: `vacancyapi_search_vacancies_aebd5333`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| start_date | query | no | string \| null |  |  |
| end_date | query | no | string \| null |  |  |
| ordering | query | no | string \| null |  | default=created_at |
| search | query | no | string \| null |  |  |
| page | query | no | integer |  | minimum=1; default=1 |
| page_size | query | no | integer \| null |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: NinjaPaginationResponseSchema_VacancyResponseSchema_ |