Feature: List products from admin UI
  As an eCommerce manager
  I need the ability to list all products from the admin UI
  So that I can view the current catalog without using the API directly

  Scenario: List all products when products exist
    Given multiple products exist in the database
    And I am on the "List Products" admin page
    When I press the "List All" button
    Then I should see all products displayed in the results area

  Scenario: Show a message when no products exist
    Given no products exist in the database
    And I am on the "List Products" admin page
    When I press the "List All" button
    Then I should see a message indicating no products were found
