from common.exceptions import ErrorCode

# Chat-specific error codes
ConversationNotFoundError = ErrorCode("conversation", "not_found")
MessageNotFoundError = ErrorCode("message", "not_found")
ConversationNotOwnedError = ErrorCode("conversation", "not_owned")
MessageNotOwnedError = ErrorCode("message", "not_owned")
InvalidParticipantError = ErrorCode("conversation", "invalid_participant")
