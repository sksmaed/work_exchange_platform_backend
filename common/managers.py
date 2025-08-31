from collections.abc import Iterable, Sequence
from typing import Any
from uuid import UUID

from django.contrib.auth.models import AbstractBaseUser
from django.db.models import Manager, QuerySet


class BaseModelManager(Manager):
    """Base model manager for all models."""

    def get_queryset(self) -> QuerySet:
        """Overwritten get_queryset method for soft delete.

        Returns:
            QuerySet: QuerySet object.
        """
        queryset = super().get_queryset()
        # Only apply is_deleted filter if the field exists on the model
        if hasattr(self.model, 'is_deleted'):
            queryset = queryset.exclude(is_deleted=True)
        return queryset

    def bulk_create(  # noqa: PLR0913
        self,
        objs: Iterable,
        batch_size: int | None = None,
        ignore_conflicts: bool = False,
        update_conflicts: bool | None = False,
        update_fields: Sequence[str] | None = None,
        unique_fields: Sequence[str] | None = None,
        user: AbstractBaseUser | UUID | str | None = None,
    ) -> list:
        """Overwritten bulk_create method for setting created_by and updated_by fields."""
        if user is not None:
            if isinstance(user, AbstractBaseUser):
                for obj in objs:
                    obj.created_by_user = user
                    obj.updated_by_user = user
            else:
                if isinstance(user, str):
                    user = UUID(user)
                for obj in objs:
                    obj.created_by_user_id = user
                    obj.updated_by_user_id = user
        return super().bulk_create(
            objs,
            batch_size,
            ignore_conflicts,
            update_conflicts,
            update_fields,
            unique_fields,
        )

    def bulk_update(
        self,
        objs: Iterable,
        fields: Sequence[str],
        batch_size: int | None = None,
        user: AbstractBaseUser | UUID | str | None = None,
    ) -> int:
        """Overwritten bulk_update method for setting updated_by field."""
        if user is not None:
            if isinstance(user, AbstractBaseUser):
                for obj in objs:
                    obj.updated_by_user = user
            else:
                if isinstance(user, str):
                    user = UUID(user)
                for obj in objs:
                    obj.updated_by_user_id = user
        return super().bulk_update(objs, fields, batch_size)

    def create(
        self,
        user: AbstractBaseUser | UUID | str | None = None,
        **kwargs: dict[str, Any],
    ):
        """Overwritten create method for setting created_by and updated_by fields."""
        if user is not None:
            if isinstance(user, AbstractBaseUser):
                kwargs.setdefault("created_by_user", user)
                kwargs.setdefault("updated_by_user", user)
            else:
                if isinstance(user, str):
                    user = UUID(user)
                kwargs.setdefault("created_by_user_id", user)
                kwargs.setdefault("updated_by_user_id", user)
        return super().create(**kwargs)

    def get_or_create(
        self,
        defaults: dict[str, Any] | None = None,
        user: AbstractBaseUser | UUID | str | None = None,
        **kwargs: dict[str, Any],
    ):
        """Overwritten get_or_create method for setting created_by and updated_by fields."""
        if user is not None:
            if defaults is None:
                defaults = {}
            if isinstance(user, AbstractBaseUser):
                defaults.setdefault("created_by_user", user)
                defaults.setdefault("updated_by_user", user)
            else:
                if isinstance(user, str):
                    user = UUID(user)
                defaults.setdefault("created_by_user_id", user)
                defaults.setdefault("updated_by_user_id", user)
        return super().get_or_create(defaults=defaults, **kwargs)
