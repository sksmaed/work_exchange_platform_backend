from common.exceptions import ErrorCode

# Forum-specific error codes
ForumThreadNotFoundError = ErrorCode("forum_thread", "not_found")
ForumReplyNotFoundError = ErrorCode("forum_reply", "not_found")
ForumThreadImageNotFoundError = ErrorCode("forum_thread_image", "not_found")
ForumReplyImageNotFoundError = ErrorCode("forum_reply_image", "not_found")
ForumInvalidImageError = ErrorCode("forum", "invalid_image")
