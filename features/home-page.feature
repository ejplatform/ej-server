Feature: View Home Page
    
    Scenario: Anonymous user accessing desktop home page

        Given an anonymous user
        When I access the desktop home page
        Then I see login button

    Scenario: Anonymous user accessing mobile home page

        Given an anonymous user
        When I access the mobile home page
        Then I see login button

    Scenario: Authenticated user accessing desktop home page

        Given an authenticated user
        Given promoted conversations
        When I access the desktop home page
        Then I see the promoted conversations
        Then I see the profile button
        Then I see the conversations button
        Then I see the side menu

    Scenario: Authenticated user accessing mobile home page

        Given an authenticated user
        Given promoted conversations
        When I access the mobile home page
        Then I see the promoted conversations
        Then I see the profile button
        Then I see the conversations button
        Then I see the hamburger menu