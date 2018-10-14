import pytest

from ej_users.models import User
from ej_profiles.models import Profile
from ej_notifications.models import Channel, Message, Notification, NotificationConfig


class TestChannelManager:
    @pytest.fixture
    def mk_user(db):
        user = User.objects.create_user('email@server.com', 'password')
        user.save()
        return user

    @pytest.fixture
    def mk_user2(db):
        user = User.objects.create_user('email@email.com', 'password')
        user.save()
        return user

    @pytest.fixture
    def mk_channel(self, mk_user):
        new_user = mk_user
        new_user.save()
        channel = Channel(
            name='channel',
            owner=new_user
        )
        channel.save()
        return channel

    def test_can_create_and_fetch_channel(self, db, mk_channel):
        channel = mk_channel
        assert channel.name == 'channel'
        assert Channel.objects.get(name='channel') == channel

    def test_set_users_in_channel(sef, db, mk_channel, mk_user):
        user = mk_user
        channel = mk_channel
        channel.users.set([user])
        assert channel.users.first() == user

    def test_send_message(self, db, mk_user, mk_user2, mk_channel):
        channel = mk_channel
        user = mk_user
        user2 = mk_user2
        channel.users.set([user, user2])
        message = Message.objects.create(channel=channel, title='title')
        notifications_user = Notification.objects.filter(receiver__id=user.id, read=False).first()
        notifications_user2 = Notification.objects.filter(receiver__id=user.id, read=False).first()

        assert notifications_user.message == message
        assert notifications_user2.message == message

    def test_ensure_settings_created(self, db, mk_user):
        user = mk_user
        user.raw_profile, created = Profile.objects.get_or_create(user=user)
        assert created
        assert NotificationConfig.objects.filter(profile=user.profile).exists()
