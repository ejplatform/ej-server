from boogie.configurations import env
from .paths import PathsConf


class ThemesConf(PathsConf):
    """
    Config for the themes
    """
    EJ_THEME = env("default", name="{attrs}")

    def finalize(self, settings):
        """
        Return the theme settings
        :param settings:
        :return: settings
        """
        theme = self.EJ_THEME
        settings = super().finalize(settings)
        if theme in ("default", None):
            return settings

        # Insert settings overrides
        print(f"Running theme: {theme}")
        path = theme if "/" in theme else self.THEMES_DIR / theme
        settings_path = path / "settings.py"

        if settings_path.exists():
            with open(settings_path) as fh:
                data = fh.read()
                globs = dict(settings)
                exec (data, globs)
                globs = {k: v for k, v in globs.items() if k.isupper()}
                settings.update(globs)

        return settings
