from common.exceptions import ErrorCode

# Application-specific error codes
ApplicationNotFoundError = ErrorCode("application", "not_found")
ApplicationAlreadyExistsError = ErrorCode("application", "already_exists")
ApplicationNotOwnedError = ErrorCode("application", "not_owned")

