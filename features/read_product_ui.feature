Feature: Read product from admin UI
  As an eCommerce manager
  I need the ability to retrieve a product by its ID on the admin UI
  So that I can quickly look up a specific product's details

  Background:
    Given a product with id "1" exists in the database

  Scenario: Retrieve an existing product from the admin interface
    Given I am on the "Read Product" admin page
    When I enter "1" in the ID field and press the "Retrieve" button
    Then the product details should be displayed in the form fields

  Scenario: Show an error for a missing product
    Given I am on the "Read Product" admin page
    When I enter "999999" in the ID field and press the "Retrieve" button
    Then I should see an error message indicating the product was not found
