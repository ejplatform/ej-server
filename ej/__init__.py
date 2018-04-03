__version__ = '0.1.0'
__version_info__ = tuple(map(int, __version__.split('.')))

from config import fixes

fixes.apply_all()
