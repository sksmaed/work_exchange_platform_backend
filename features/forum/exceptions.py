from common.exceptions import ErrorCode

# Forum-specific error codes
ForumCategoryNotFoundError = ErrorCode("forum_category", "not_found")
ForumThreadNotFoundError = ErrorCode("forum_thread", "not_found")
ForumReplyNotFoundError = ErrorCode("forum_reply", "not_found")
ForumThreadImageNotFoundError = ErrorCode("forum_thread_image", "not_found")
ForumReplyImageNotFoundError = ErrorCode("forum_reply_image", "not_found")
ForumThreadNotOwnedError = ErrorCode("forum_thread", "not_owned")
ForumReplyNotOwnedError = ErrorCode("forum_reply", "not_owned")
ForumInvalidImageError = ErrorCode("forum", "invalid_image")
