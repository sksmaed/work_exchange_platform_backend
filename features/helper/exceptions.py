from common.exceptions import ErrorCode

# Helper-specific error codes
HelperNotFoundError = ErrorCode("helper", "not_found")
HelperAlreadyExistsError = ErrorCode("helper", "already_exists")

