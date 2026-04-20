Feature: Purchase product from admin UI
  As an eCommerce manager
  I need the ability to purchase a product from the admin UI
  So that stock quantity is decremented and availability is updated automatically without using the API directly

  Background:
    Given a product with id "1" exists and has a stock quantity of 5

  Scenario: Purchase an in-stock product from the admin interface
    Given I am on the "Purchase Product" admin page
    When I enter "1" in the ID field
    And I press the "Purchase" button
    Then the stock quantity should be decremented to 4
    And I should see the updated product details
    And I should see a success message

  Scenario: Show an error for an unavailable or out-of-stock product
    Given I am on the "Purchase Product" admin page
    And product "1" is unavailable or has a stock quantity of 0
    When I enter "1" in the ID field
    And I press the "Purchase" button
    Then I should see an error message indicating the product is not available for purchase
