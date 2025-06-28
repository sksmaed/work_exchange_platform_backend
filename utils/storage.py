from pathlib import Path
from uuid import uuid4

from django.db import models
from inflection import dasherize, underscore


def get_model_file_path(instance: models.Model, filename: str) -> Path:
    """Generate a file path for the uploaded file of model."""
    return (
        Path(dasherize(instance._meta.app_label))
        / dasherize(underscore(instance.__class__.__name__))
        / f"{uuid4()}{Path(filename).suffix}"
    )
