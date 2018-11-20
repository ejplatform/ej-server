from behave import when


@when('I access the desktop home page')
def access_desktop_home_page(context):
    browser = context.browser
    browser.driver.set_window_size(1024, 1366)
    browser.visit(context.base_url)


@when('I access the mobile home page')
def access_mobile_home_page(context):
    browser = context.browser
    browser.driver.set_window_size(375, 812)
    browser.visit(context.base_url)
