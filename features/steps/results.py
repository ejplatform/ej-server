from behave import then
from util import find_by_css


@then('I see login button')
def see_login_button(context):
    find_by_css(context, '.Header-lowerNotLogged')


@then('I see the promoted conversations')
def see_promoted_conversations(context):
    # context.browser.screenshot(full=True)
    find_by_css(context, '.ConversationCard-container')


@then('I see the profile button')
def see_profile_button(context):
    find_by_css(context, '.profile-link')


@then('I see the side menu')
def see_the_side_menu(context):
    find_by_css(context, '.NavMenu')


@then('I see the conversations button')
def see_conversations_button(context):
    find_by_css(context, '.conversations-link')
