from typing import Any, ClassVar
from uuid import UUID, uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from common.managers import BaseModelManager


class BaseModel(models.Model):
    """Abstract base model providing UUID primary key, audit fields, and custom manager.

    Attributes:
    ----------
    id : UUIDField
        Unique identifier for each instance.
    created_at : DateTimeField
        Timestamp when the instance was created.
    created_by_user : ForeignKey
        User who created the instance.
    updated_at : DateTimeField
        Timestamp when the instance was last updated.
    updated_by_user : ForeignKey
        User who last updated the instance.
    objects : BaseModelManager
        Custom manager for the model.
    """

    id = models.UUIDField(primary_key=True, unique=True, default=uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="%(class)s_created_by_user",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by_user",
    )
    objects = BaseModelManager()

    class Meta:
        abstract = True

    class ExtraMeta:
        date_filter_fields: ClassVar[list[str]] = []

    DEFAULT_EXCLUDE_FIELDS: ClassVar = [
        "created_at",
        "created_by_user",
        "updated_at",
        "updated_by_user",
    ]
    DEFAULT_GET_EXCLUDE_FIELDS = DEFAULT_EXCLUDE_FIELDS
    DEFAULT_UPDATE_EXCLUDE_FIELDS: ClassVar = [*DEFAULT_EXCLUDE_FIELDS, "id"]
    DEFAULT_CREATE_EXCLUDE_FIELDS: ClassVar = [*DEFAULT_EXCLUDE_FIELDS, "id"]

    def save(
        self,
        user: AbstractBaseUser | UUID | str | None = None,
        *args: list[Any],
        **kwargs: dict[Any, Any],
    ):
        """Save and update the object with user information.

        This method saves or updates the object and sets the 'updated_by_user' field to the specified user.
        Additionally, any extra keyword arguments provided will be applied to the object.

        Args:
            user (AbstractBaseUser | UUID | str | None): The user responsible for the update.
            *args (list[Any]): Additional positional arguments.
            **kwargs (dict[Any, Any]): Additional keyword arguments to be applied to the object.

        Returns:
            None

        """
        if user is not None:
            if isinstance(user, AbstractBaseUser):
                if self._state.adding:
                    self.created_by_user = user
                self.updated_by_user = user
            else:
                if isinstance(user, str):
                    user = UUID(user)
                if self._state.adding:
                    self.created_by_user_id = user
                self.updated_by_user_id = user
        super().save(*args, **kwargs)  # type: ignore
