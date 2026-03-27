# applications

## POST `/api/applications`

- - Operation ID: `applicationapi_create_application_d1d76461` - Request Body | Content Type | Schema | Required | | --- | --- | --- | | `application/json` | `ApplicationCreateSchema` | yes | - Responses | Status | Description | Content | | --- | --- | --- | | 201 | Created | application/json: ApplicationResponseSchema |

## DELETE `/api/applications/{application_id}`

- - Operation ID: `applicationapi_withdraw_application_ccc6a838` - Parameters | Name | In | Required | Type | Description | Constraints | | --- | --- | --- | --- | --- | --- | | application_id | path | yes | string | | | - Responses | Status | Description | Content | | --- | --- | --- | | 200 | OK | application/json: object |

## GET `/api/applications/{application_id}`

- - Operation ID: `applicationapi_get_application_fa27cb50` - Parameters | Name | In | Required | Type | Description | Constraints | | --- | --- | --- | --- | --- | --- | | application_id | path | yes | string | | | - Responses | Status | Description | Content | | --- | --- | --- | | 200 | OK | application/json: ApplicationResponseSchema |

## PATCH `/api/applications/{application_id}/status`

- - Operation ID: `applicationapi_update_application_status_405eba4f` - Parameters | Name | In | Required | Type | Description | Constraints | | --- | --- | --- | --- | --- | --- | | application_id | path | yes | string | | | - Request Body | Content Type | Schema | Required | | --- | --- | --- | | `application/json` | `ApplicationStatusUpdateSchema` | yes | - Responses | Status | Description | Content | | --- | --- | --- | | 200 | OK | application/json: ApplicationResponseSchema |

## GET `/api/applications/self/`

- - Operation ID: `applicationapi_get_self_applications_be27cd6d` - Responses | Status | Description | Content | | --- | --- | --- | | 200 | OK | application/json: array[ApplicationResponseSchema] |