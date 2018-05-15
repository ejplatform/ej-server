from splinter import Browser

def test_signup(browser):
    # Visit URL
    url = "http://localhost:8000/profile/"
    browser.visit(url)
    
    browser.click_link_by_partial_href("/register/")

    browser.type('name', "Rodrigo Teste")
    browser.type('email', "teste123@gmail.com")
    browser.type('password', "1213123")
    browser.type('password_confirm', "1213123")
    browser.find_by_name('register').first.click()

    print(browser.driver.current_url)
    if "register" not in browser.driver.current_url and "profile" in browser.driver.current_url:
        #browser.find_by_value("Sair").first.click()
        return True
    else:
        browser.driver.save_screenshot('signup_test_fail.png')
        return False

with Browser("firefox") as browser:
    assert test_signup(browser)
    # assert test_login()
