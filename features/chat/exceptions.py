from common.exceptions import ErrorCode

# Chat-specific error codes
ConversationNotFoundError = ErrorCode("conversation", "not_found")
InvalidParticipantError = ErrorCode("conversation", "invalid_participant")
