from behave import given
from ej_users.models import User
from ej_conversations import create_conversation


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


@given('promoted conversations')
def given_promoted_conversations(context):
    staff_user = User.objects.create_user('staff@email.com', 'test', is_staff=True)
    create_conversation(
        'This is a conversation for test',
        'Testing',
        is_promoted=True,
        author=staff_user,
    )
    create_conversation(
        'This is also a conversation for test',
        'Still Testing',
        is_promoted=True,
        author=staff_user,
    )
