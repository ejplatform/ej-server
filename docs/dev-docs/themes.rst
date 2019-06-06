Themes
======

The EJ platform has a theme structure that can be easily tweaked and adapted
for different instances.


Running different themes
------------------------

The theme is controlled by a environment variable. A new theme can
be chosen by setting ``EJ_THEME`` to name or path to the desired theme::

    $ export EJ_THEME=cpa

We've implemented a few default themes at /lib/themes/. Those themes are also
a good reference of what can be done within the theme structure.

Once this variable is set, the CSS will be built using the desired theme. The
theme can also override static assets and even Django settings.


Creating a new theme for the EJ platform
----------------------------------------

A theme is organized within the following file structure::

    - <theme-name>
        |- assets/   (overrides default assets)
        \- scss/
            |- _overrides.scss (overrides SASS variables)
            |- main.scss
            \- rocket.scss

Both main.scss and rocket.scss have standard implementations and can be simply
copied from one theme to the other. Most of your work will probably concentrate
in the _settings.scss file: it defines all overrides of scss variables and can
be used to declare colors, fonts, layouts, spacing, etc.
