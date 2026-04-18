Feature: Delete product from admin UI
  As an eCommerce manager
  I need to delete a product from the admin UI
  So that I can remove products that should no longer appear in the catalog

  Background:
    Given a product with id "1" exists in the database

  Scenario: Delete an existing product from the admin interface
    Given I am on the "Delete Product" admin page
    When I enter "1" in the ID field
    And I press the "Delete" button
    Then the product should be deleted successfully
    And I should see a success message indicating the product was removed

  Scenario: Show an error for a missing product
    Given I am on the "Delete Product" admin page
    When I enter "999999" in the ID field
    And I press the "Delete" button
    Then I should see an error message indicating the product was not found
