from selenium.webdriver.common.keys import Keys
from splinter import Browser
import pytest
import os

from ej_conversations import create_conversation
from ej_users.models import User


@pytest.fixture
def user(db):
    user = User.objects.create_user('email@server.com', 'password')
    create_conversation(text='test', title='title', author=user,
                        is_promoted=True)
    return user


@pytest.fixture
def driver():
    # create fake browser
    window = Browser('chrome', headless=True)
    yield window
    window.quit()


class TestUIVote:
    """
    Test UI when a user try to vote after register and after the login.
    """
    @pytest.mark.skipif(os.environ.get('EJ_BASE_URL') != 'localhost',
                        reason="selenium tests only run in localhost yet")
    def test_user_vote_after_login(self, live_server, driver, user):
        # list conversations and click on the first
        driver.visit(f'{live_server.url}/conversations/')
        driver.find_by_text('test').click()
        driver.find_by_text('login').click()
        assert driver.url == f'{live_server.url}/login/'

        # login with user created
        driver.find_by_name('email').fill('email@server.com')
        driver.find_by_name('password').fill('password')
        driver.find_by_name('login')._element.send_keys(Keys.SPACE)

        assert driver.url == f'{live_server.url}/conversations/'
