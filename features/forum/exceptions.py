from common.exceptions import ErrorCode

# Forum-specific error codes
ForumCategoryNotFoundError = ErrorCode("forum_category", "not_found")
ForumThreadNotFoundError = ErrorCode("forum_thread", "not_found")
ForumReplyNotFoundError = ErrorCode("forum_reply", "not_found")
ForumThreadNotOwnedError = ErrorCode("forum_thread", "not_owned")
ForumReplyNotOwnedError = ErrorCode("forum_reply", "not_owned")
