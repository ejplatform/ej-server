import os
import pathlib

from boogie.configurations import PathsConf as Base, env


class PathsConf(Base):
    REPO_DIR = pathlib.Path(__file__).parent.parent.parent.parent
    ROOT_DIR = SRC_DIR = APPS_DIR = REPO_DIR / 'src'
    PROJECT_DIR = ROOT_DIR / 'ej'

    # Local paths
    LOCAL_DIR = REPO_DIR / 'local'
    DB_DIR = LOCAL_DIR / 'db'
    MEDIA_ROOT = env(LOCAL_DIR / 'media')
    STATIC_ROOT = env(LOCAL_DIR / 'static')
    FRAGMENTS_DIR = LOCAL_DIR / 'fragments'
    PAGES_DIR = LOCAL_DIR / 'pages'

    # Frontend paths
    LIB_DIR = REPO_DIR / 'lib'

    # Static files
    STATICFILES_DIRS = [REPO_DIR / 'lib/assets']

    def finalize(self, settings):
        """
        Create missing paths.
        """
        for path in [self.LOCAL_DIR, self.DB_DIR, self.MEDIA_ROOT,
                     self.STATIC_ROOT]:
            if not os.path.exists(path):
                mkdir_recursive(path)

        return super().finalize(settings)


def mkdir_recursive(path):
    # TODO: implement recursive dir creation.
    print(f'making required directory: {path}')
    os.mkdir(path)
