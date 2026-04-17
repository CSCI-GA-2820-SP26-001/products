Feature: Update product from admin UI
  As an eCommerce manager
  I need to update an existing product from the admin UI
  So that I can correct product information without using the API directly

  Background:
    Given a product with id "1" exists in the database

  Scenario: Update an existing product from the admin interface
    Given I am on the "Update Product" admin page
    When I retrieve product "1"
    And I modify one or more fields
    And I press the "Update" button
    Then the product should be updated successfully
    And I should see a success message
    And I should see the updated product details

  Scenario: Show an error for a missing product
    Given I am on the "Update Product" admin page
    When I retrieve product "999999"
    Then I should see an error message indicating the product was not found
