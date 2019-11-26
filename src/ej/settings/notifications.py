from boogie.configurations import Conf, env


class NotificationsConf(Conf):
    """
    This class is responsible for the notification of the app using the fcm an app for Firebase Cloud Messaging.
    Used as an unified platform for sending push notifications to mobile devices (android / ios).
    https://fcm-django.readthedocs.io/en/latest/
    """
    EJ_PUSH_NOTIFICATIONS = env("none", name="{name}")

    def get_push_notifications_settings(self, ej_push_notifications):
        """
        This receives the ej_push_notifications it must be either none or fcm
        :param ej_push_notifications:
        :return: FCM_API_KEY if fcm or none if none
        """
        if ej_push_notifications == "none":
            return {}
        elif ej_push_notifications == "fcm":
            return {"FCM_API_KEY": self.FCM_API_KEY}
        else:
            raise ValueError(f"invalid value for EJ_PUSH_NOTIFICATIONS = {ej_push_notifications}")

    FCM_API_KEY = env(
        (
            "AAAA8tCCQJQ:APA91bHDVVtaPzYFjyDzQTWiTAqrzPcswYV8NuQLhh"
            "vkn6s4H0Z69dYvWeyHUSPXFxV-8Ns6zvrffqRZ-_URuPxgvWXCfqOJi"
            "-BBlFzkHcvK97O9d8Ju1pgHBWQml9DQY9QWSoroc5Sl"
        )
    )
