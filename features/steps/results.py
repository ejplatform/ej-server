from behave import then
from util import find_by_css


@then('I see login button')
def see_login_button(context):
    find_by_css(context, '.Header-lowerNotLogged')


@then('I see the conversations')
def see_conversations(context):
    find_by_css(context, '.Page home')
    find_by_css(context, '.ConversationCard-container')


@then('I see the profile button')
def see_profile_button(context):
    find_by_css(context, '.profile-link')


@then('I see the side menu')
def see_the_side_menu(context):
#     b = context.browser
#     e = b.find_by_css('.NavMenu')
#     print(e)
#     assert e
    find_by_css(context, '.NavMenu')
