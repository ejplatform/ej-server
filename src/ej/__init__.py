import os
from .fixes import apply_all

__all__ = []

if os.environ.get("EXPERIMENTAL_ACCELERATE", "true").lower() == "true":
    from ej.fixes.startup_accelerator import accelerate

    accelerate()


# Apply fixes
apply_all()
