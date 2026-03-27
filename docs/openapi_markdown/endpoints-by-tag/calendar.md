# calendar

## DELETE `/api/calendar/events/{event_id}`

- Host deletes a calendar event.
- Operation ID: `calendarapi_delete_calendar_event_6c74d116`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| event_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: object |

## PATCH `/api/calendar/events/{event_id}`

- Host updates a calendar event (e.g., modifying dates or remarks).
- Operation ID: `calendarapi_update_calendar_event_7b121c91`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| event_id | path | yes | string |  |  |


- Request Body

| Content Type | Schema | Required |
| --- | --- | --- |
| `application/json` | `CalendarEventUpdateSchema` | yes |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: CalendarEventResponseSchema |

## GET `/api/calendar/hosts/{host_id}/events`

- Retrieve a list of calendar events for a specific host.
- Operation ID: `calendarapi_list_calendar_events_1b6cdf5b`
- Parameters

| Name | In | Required | Type | Description | Constraints |
| --- | --- | --- | --- | --- | --- |
| host_id | path | yes | string |  |  |


- Responses

| Status | Description | Content |
| --- | --- | --- |
| 200 | OK | application/json: array[CalendarEventResponseSchema] |