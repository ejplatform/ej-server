Feature: View Home Page
    
    Scenario: Anonymous user access index page

    Given an anonymous user
    When I access the desktop home page
    Then I see login button

    Scenario: Logged in user access index page

    Given an authenticated user
    When I access the desktop home page
    Then I see the conversations
    Then I see the profile button
    Then I see the side menu