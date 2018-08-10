from boogie.configurations import env
from .paths import PathsConf


class ThemesConf(PathsConf):
    EJ_THEME = env('default', name='{attrs}')

    def finalize(self, settings):
        theme = self.EJ_THEME
        settings = super().finalize(settings)
        if theme in ('default', None):
            return settings

        # Insert settings overrides
        path = theme if '/' in theme else self.THEMES_DIR / theme
        settings_path = path / 'settings.py'
        assets_path = path / 'assets'

        if settings_path.exists():
            with open(settings_path) as fh:
                data = fh.read()
                globs = dict(settings)
                exec(data, globs)
                globs = {k: v for k, v in globs.items() if k.isupper()}
                settings.update(globs)

        # Insert assets into
        dirs = settings.setdefault('STATICFILES_DIRS', [])
        if assets_path.exists():
            dirs.insert(0, assets_path)

        return settings
