Feature: BDD test environment setup
  As a developer
  I need Behave configured with Selenium
  So that the team can run UI-based BDD tests

  Scenario: Open the list products admin page
    Given I am on the "List Products" admin page
    Then I should see the heading "List Products"
    And I should see the button with id "list-all-button"

  Scenario: Open the purchase product admin page
    Given I am on the "Purchase Product" admin page
    Then I should see the heading "Purchase Product"
    And I should see the button with id "purchase-button"