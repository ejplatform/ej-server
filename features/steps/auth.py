from behave import given
from ej_users.models import User


@given('an anonymous user')
def given_anonymous_user(context):
    pass


@given('an authenticated user')
def given_auth_user(context):
    user = User.objects.create_user('test@email.com', 'test')
    user.save()

    browser = context.browser
    browser.visit(context.base_url + '/login/')
    browser.fill('email', 'test@email.com')
    browser.fill('password', 'test')
    browser.find_by_name('login').first.click()
