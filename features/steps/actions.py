from behave import when


@when('I access the desktop home page')
def access_desktop_home_page(context):
    browser = context.browser
    browser.visit(context.base_url)
