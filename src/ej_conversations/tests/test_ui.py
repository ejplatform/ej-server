from selenium.webdriver.common.keys import Keys
from splinter import Browser
import pytest
import time
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
        conv = driver.find_by_text('test')
        search_login = lambda : driver.find_by_xpath('//div[@class="Header-lowerNotLogged"]')
        if conv and search_login():
            conv.first.click()
            search_login().first.double_click()
            time.sleep(1) # wait page load
            assert f'{live_server.url}/login/' in driver.url
        else:
            pytest.fail('Couln\'t find conversation title or login button.')

        # login with user created
        email_f = driver.find_by_name('email')
        pass_f = driver.find_by_name('password')
        login_button = driver.find_by_name('login')
        if email_f and pass_f and login_button:
            email_f.first.fill('email@server.com')
            pass_f.first.fill('password')
            login_button.first._element.send_keys(Keys.SPACE)
            assert driver.url == f'{live_server.url}/conversations/title/'
        else:
            pytest.fail('Couln\'t find email, password field or login button.')
