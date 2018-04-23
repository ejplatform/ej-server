from . import api_views as views


def register(router):
    router.register(r'social_media', views.SocialMediaViewSet)
    router.register(r'color_pallet', views.ColorPalletViewSet)
