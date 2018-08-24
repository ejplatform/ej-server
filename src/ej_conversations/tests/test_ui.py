from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import pytest
import os

from ej_conversations import create_conversation
from ej_users.models import User


@pytest.fixture()
def user(db):
    user = User.objects.create_user('email@server.com', 'password')
    create_conversation(text='test', title='title', author=user,
                        is_promoted=True)
    return user


@pytest.fixture(scope='module')
def driver(request):
    # create the fake browser
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    try:
        wd = webdriver.Chrome(options=chrome_options)
    except WebDriverException:
        raise AssertionError('Binário do Chrome não encontrado no PATH.')
    # wait up to 10 seconds for the elements to become available
    wd.implicitly_wait(10)
    yield wd
    wd.quit()


class TestUIVote:
    """
    Test UI when a user try to vote after register and after the login.
    """
    @pytest.mark.skipif(os.environ.get('EJ_BASE_URL') != 'localhost',
                        reason="selenium tests only run in localhost yet")
    def test_user_vote_after_login(self, live_server, driver, user):
        # list conversations and click on the first
        driver.get(f'{live_server.url}/conversations/')
        xpath_conv = '//a[contains(text(), "test")]'
        driver.find_element_by_xpath(xpath_conv).click()
        xpath_login = '//a[contains(text(), "login")]'
        driver.find_element_by_xpath(xpath_login).click()
        assert driver.current_url == f'{live_server.url}/login/'

        # login with user created
        email = driver.find_element_by_css_selector('input[name=email]')
        pw = driver.find_element_by_css_selector('input[name=password]')
        login = driver.find_element_by_css_selector('input[name=login]')

        email.send_keys('email@server.com')
        pw.send_keys('password')
        login.send_keys(Keys.ENTER)

        assert driver.current_url == f'{live_server.url}/conversations/'
