Feature: Create product from admin UI
  As an eCommerce manager
  I need to create a new product from the admin UI
  So that I can add new products to the catalog without using the API directly

  Scenario: Create a new product from the admin interface
    Given I am on the "Create Product" admin page
    When I fill in the product details
    And I press the "Create" button
    Then a new product should be created successfully
    And I should see a success message
    And I should see the created product details

  Scenario: Show an error for missing required fields
    Given I am on the "Create Product" admin page
    When I press the "Create" button without filling in required fields
    Then I should see an error message indicating the missing fields
