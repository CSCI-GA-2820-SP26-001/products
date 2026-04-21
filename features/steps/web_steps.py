"""
Step definitions for BDD Selenium setup checks
"""
from behave import given, then
from selenium.webdriver.common.by import By


PAGE_URLS = {
    "List Products": "/admin/products/list",
    "Purchase Product": "/admin/products/purchase",
    "Create Product": "/admin/products/create",
    "Read Product": "/admin/products/read",
    "Update Product": "/admin/products/update",
    "Delete Product": "/admin/products/delete",
}


@given('I am on the "{page_name}" admin page')
def step_open_admin_page(context, page_name):
    """Open the requested admin page."""
    path = PAGE_URLS[page_name]
    context.driver.get(f"{context.base_url}{path}")


@then('I should see the heading "{heading_text}"')
def step_see_heading(context, heading_text):
    """Verify the page heading is visible."""
    heading = context.driver.find_element(By.TAG_NAME, "h1")
    assert heading.text.strip() == heading_text, (
        f'Expected heading "{heading_text}" but found "{heading.text.strip()}"'
    )


@then('I should see the button with id "{button_id}"')
def step_see_button(context, button_id):
    """Verify a button exists on the page."""
    button = context.driver.find_element(By.ID, button_id)
    assert button.is_displayed(), f'Button with id "{button_id}" is not visible'