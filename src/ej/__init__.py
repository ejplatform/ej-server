import os

__all__ = []

# Conditionally enable experimental features.
if os.environ.get('EXPERIMENTAL_ACCELERATE', 'false').lower() == 'true':
    from ej.fixes.startup_accelerator import accelerate

    accelerate()

# Conditionally enable experimental features.
if os.environ.get('CELERY', 'false').lower() == 'true':
    from .celery import app as celery_app

    __all__.append('celery_app')
