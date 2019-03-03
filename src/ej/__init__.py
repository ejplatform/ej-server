import os

__all__ = []

if os.environ.get('EXPERIMENTAL_ACCELERATE', 'true').lower() == 'true':
    from ej.fixes.startup_accelerator import accelerate
    accelerate()

