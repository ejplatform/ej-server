from pymongo import MongoClient

from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from constance import config


@receiver(user_logged_out)
def logout(sender, user, request, **kwargs):
    client = MongoClient(config.MONGO_URL)
    mongo = client.rocketchat

    mongo.users.update(
        {'username': request.user.username},
        {'$set':
            {'services':
                {'iframe':
                    {'token': ''}
                }
            }
        }
    )
