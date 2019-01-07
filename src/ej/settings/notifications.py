from boogie.configurations import Conf, env


class NotificationsConf(Conf):

    EJ_PUSH_NOTIFICATIONS = env('none', name='{name}')

    def get_push_notifications_settings(self, ej_push_notifications):
        if ej_push_notifications == 'none':
            return {}
        elif ej_push_notifications == 'fcm':
            return {
                'FCM_API_KEY': self.FCM_API_KEY
            }
        else:
            raise ValueError(f'invalid value for EJ_PUSH_NOTIFICATIONS = {ej_push_notifications}')

    FCM_API_KEY = env(("AAAA8tCCQJQ:APA91bHDVVtaPzYFjyDzQTWiTAqrzPcswYV8NuQLhh"
                       "vkn6s4H0Z69dYvWeyHUSPXFxV-8Ns6zvrffqRZ-_URuPxgvWXCfqOJi"
                       "-BBlFzkHcvK97O9d8Ju1pgHBWQml9DQY9QWSoroc5Sl"))
