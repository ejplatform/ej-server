import os
import pathlib

from boogie.configurations import PathsConf as Base, env


class PathsConf(Base):
    """
    Paths for the folders of the project
    """
    BASE_DIR = REPO_DIR = pathlib.Path(__file__).parent.parent.parent.parent
    ROOT_DIR = SRC_DIR = APPS_DIR = REPO_DIR / "src"
    PROJECT_DIR = ROOT_DIR / "ej"

    # Local paths
    LOCAL_DIR = REPO_DIR / "local"
    DB_DIR = LOCAL_DIR / "db"
    MEDIA_ROOT = env(LOCAL_DIR / "media")
    STATIC_ROOT = env(LOCAL_DIR / "static")
    FRAGMENTS_DIR = LOCAL_DIR / "fragments"
    PAGES_DIR = LOCAL_DIR / "pages"
    LOG_DIR = LOCAL_DIR / "logs"
    LOG_FILE_PATH = LOG_DIR / "logfile.log"
    ROOT_TEMPLATE_DIR = PROJECT_DIR / "templates"

    # Frontend paths
    LIB_DIR = REPO_DIR / "lib"
    LIB_BUILD = LIB_DIR / "build"
    THEMES_DIR = LIB_DIR / "themes"

    def finalize(self, settings):
        """
        Return the paths for
            self.LOCAL_DIR,
            self.DB_DIR,
            self.MEDIA_ROOT,
            self.STATIC_ROOT,
            self.LOG_DIR,
            self.LIB_DIR,
            self.LIB_BUILD,
        :param settings:
        :return: settings
        """
        for path in [
            self.LOCAL_DIR,
            self.DB_DIR,
            self.MEDIA_ROOT,
            self.STATIC_ROOT,
            self.LOG_DIR,
            self.LIB_DIR,
            self.LIB_BUILD,
        ]:
            if not os.path.exists(path):
                mkdir_recursive(path)

        return super().finalize(settings)

    def get_staticfiles_dirs(self, repo_dir):
        """
        It return that path for the dirs that contains static files
        lib/build
        lib/assets

        :param repo_dir:
        :return: dirs
        """
        dirs = [repo_dir / "lib/build", repo_dir / "lib/assets"]
        if self.EJ_THEME:
            path = self.EJ_THEME_PATH / "assets"
            if path.exists():
                dirs.insert(0, path)
        return dirs

    def get_django_templates_dirs(self):
        """
        Return the path for the template dirs
        :return: dirs
        """
        dirs = [self.ROOT_TEMPLATE_DIR / "django"]
        if self.EJ_THEME:
            dirs.insert(0, self.EJ_THEME_PATH / "templates" / "django")
        return dirs

    def get_jinja_templates_dirs(self):
        """
        Return  the path for the jinja2 dirs
        :return: dirs
        """
        dirs = [self.ROOT_TEMPLATE_DIR / "jinja2"]
        if self.EJ_THEME:
            dirs.insert(0, self.EJ_THEME_PATH / "templates" / "jinja2")
        return dirs

    def get_ej_theme_path(self):
        """
        Return  the path for the theme dirs
        :return: dirs
        """
        if os.path.sep in self.EJ_THEME:
            return self.EJ_THEME
        else:
            return self.THEMES_DIR / self.EJ_THEME


def mkdir_recursive(path):
    # TODO: implement recursive dir creation.
    print(f"making required directory: {path}")
    os.mkdir(path)
