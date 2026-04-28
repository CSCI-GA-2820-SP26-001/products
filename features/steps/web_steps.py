"""
Web step definitions for admin UI BDD tests.

Every step here drives the admin web pages through Selenium (with
WebDriverWait + expected_conditions). No direct REST/API calls are issued
from this module.
"""

# pylint: disable=not-callable,no-name-in-module
from behave import given, then, when
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


PAGE_URLS = {
    "List Products": "/admin/products/list",
    "Purchase Product": "/admin/products/purchase",
    "Create Product": "/admin/products/create",
    "Read Product": "/admin/products/read",
    "Update Product": "/admin/products/update",
    "Delete Product": "/admin/products/delete",
}

BUTTON_IDS = {
    "Create": "create-button",
    "Retrieve": "retrieve-button",
    "Update": "update-button",
    "Delete": "delete-button",
    "Purchase": "purchase-button",
    "List All": "list-all-button",
    "Query": "query-button",
}

ID_INPUTS_BY_PATH = {
    "/admin/products/read": "retrieve-product-id",
    "/admin/products/update": "retrieve-product-id",
    "/admin/products/delete": "delete-product-id",
    "/admin/products/purchase": "purchase-product-id",
}

ERROR_PHRASE_PATTERNS = {
    "the missing fields": ["required", "missing", "valid"],
    "the product was not found": ["not found"],
    "the product was removed": ["deleted", "removed"],
    "the product is not available for purchase": [
        "not available",
        "out of stock",
        "unavailable",
    ],
}


def _wait(context):
    return WebDriverWait(context.driver, context.wait_seconds)


def _resolve_id(context, alias):
    """Return the real product id for a feature-file alias, or the alias itself."""
    return context.products.get(alias, alias)


def _id_input_for_current_page(context):
    url = context.driver.current_url
    for path, input_id in ID_INPUTS_BY_PATH.items():
        if path in url:
            return input_id
    raise RuntimeError(f"No ID input mapping for current page: {url}")


def _message_class(driver):
    return driver.find_element(By.ID, "message").get_attribute("class") or ""


def _message_text(driver):
    return driver.find_element(By.ID, "message").text or ""


def _details_lookup(driver, container_id):
    """Return a dict mapping detail label (lower) -> value text."""
    container = driver.find_element(By.ID, container_id)
    dt_elements = container.find_elements(By.TAG_NAME, "dt")
    dd_elements = container.find_elements(By.TAG_NAME, "dd")
    return {
        label.text.strip().lower(): value.text.strip()
        for label, value in zip(dt_elements, dd_elements)
    }


######################################################################
# Page navigation and basic visibility
######################################################################


@given('I am on the "{page_name}" admin page')
def step_open_admin_page(context, page_name):
    """Open the requested admin page."""
    path = PAGE_URLS[page_name]
    context.driver.get(f"{context.base_url}{path}")


@then('I should see the heading "{heading_text}"')
def step_see_heading(context, heading_text):
    """Verify the page heading is visible."""
    heading = _wait(context).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert heading.text.strip() == heading_text, (
        f'Expected heading "{heading_text}" but found "{heading.text.strip()}"'
    )


@then('I should see the button with id "{button_id}"')
def step_see_button(context, button_id):
    """Verify a button exists on the page."""
    button = _wait(context).until(
        EC.presence_of_element_located((By.ID, button_id))
    )
    assert button.is_displayed(), f'Button with id "{button_id}" is not visible'


######################################################################
# Form interactions
######################################################################


@when('I fill in the product details')
def step_fill_product_details(context):
    """Populate the Create Product form with a known payload."""
    payload = {
        "name": "BDD Created Product",
        "description": "Created via Selenium BDD",
        "price": "12.34",
        "category": "BDD Category",
        "stock": "7",
        "available": True,
    }
    context.created_payload = payload

    driver = context.driver
    for field_id in ("name", "description", "price", "category", "stock"):
        element = driver.find_element(By.ID, field_id)
        element.clear()
        element.send_keys(payload[field_id])

    available_input = driver.find_element(By.ID, "available")
    if payload["available"] != available_input.is_selected():
        available_input.click()


@when('I press the "{button}" button')
def step_press_button(context, button):
    """Click a labelled action button on the current page."""
    button_id = BUTTON_IDS[button]
    _wait(context).until(EC.element_to_be_clickable((By.ID, button_id))).click()


@when('I press the "{button}" button without filling in required fields')
def step_press_button_no_fill(context, button):
    """Click submit with empty required fields and capture HTML5 validity."""
    button_id = BUTTON_IDS[button]
    context.driver.find_element(By.ID, button_id).click()
    name_field = context.driver.find_element(By.ID, "name")
    context.html5_validation_triggered = bool(
        context.driver.execute_script(
            "return arguments[0].validity.valueMissing;", name_field
        )
    )


@when('I enter "{alias}" in the ID field')
def step_enter_id(context, alias):
    """Type the resolved id into the ID input on the current page."""
    real_id = _resolve_id(context, alias)
    input_id = _id_input_for_current_page(context)
    field = _wait(context).until(EC.presence_of_element_located((By.ID, input_id)))
    field.clear()
    field.send_keys(str(real_id))


@when('I enter "{alias}" in the ID field and press the "{button}" button')
def step_enter_id_and_press(context, alias, button):
    """Combine entering an id and pressing an action button."""
    step_enter_id(context, alias)
    step_press_button(context, button)


@when('I enter "{category}" in the category field and press the "{button}" button')
def step_enter_category_and_press(context, category, button):
    """Type a category name into the list page filter and press a button."""
    field = _wait(context).until(
        EC.presence_of_element_located((By.ID, "category-input"))
    )
    field.clear()
    field.send_keys(category)
    step_press_button(context, button)


@when('I retrieve product "{alias}"')
def step_retrieve_product(context, alias):
    """Drive the Retrieve flow on the Update Product page."""
    real_id = _resolve_id(context, alias)
    field = _wait(context).until(
        EC.presence_of_element_located((By.ID, "retrieve-product-id"))
    )
    field.clear()
    field.send_keys(str(real_id))
    context.driver.find_element(By.ID, "retrieve-button").click()
    _wait(context).until(
        lambda d: "success" in _message_class(d) or "error" in _message_class(d)
    )


@when('I modify one or more fields')
def step_modify_fields(context):
    """Append a known suffix to the name field to track an update."""
    name_field = context.driver.find_element(By.ID, "name")
    current = name_field.get_attribute("value") or "Product"
    new_name = f"{current} (updated)"
    name_field.clear()
    name_field.send_keys(new_name)
    context.updated_name = new_name


######################################################################
# Outcome assertions
######################################################################


@then('a new product should be created successfully')
def step_created_successfully(context):
    """Wait for the created-product card to be revealed."""
    _wait(context).until(
        lambda d: "hidden"
        not in (d.find_element(By.ID, "created-product").get_attribute("class") or "")
    )


@then('I should see a success message')
def step_see_success_message(context):
    """Wait for #message to gain the success class."""
    _wait(context).until(lambda d: "success" in _message_class(d))


@then('I should see an error message indicating {phrase}')
def step_see_error_message(context, phrase):
    """Wait for #message to gain the error class with an expected phrase."""
    needle = phrase.strip().strip('"')
    patterns = ERROR_PHRASE_PATTERNS.get(needle, [needle.lower()])

    if needle == "the missing fields" and getattr(
        context, "html5_validation_triggered", False
    ):
        return

    def _check(driver):
        try:
            cls = _message_class(driver)
            text = _message_text(driver).lower()
            if "error" not in cls:
                return False
            return any(p in text for p in patterns)
        except Exception:  # pylint: disable=broad-except
            return False

    _wait(context).until(_check)


@then('I should see the created product details')
def step_see_created_details(context):
    """Verify the created-product details card shows the expected name."""
    _wait(context).until(
        lambda d: "hidden"
        not in (d.find_element(By.ID, "created-product").get_attribute("class") or "")
    )
    details = _details_lookup(context.driver, "created-product-details")
    expected_name = context.created_payload["name"]
    assert details.get("name") == expected_name, (
        f"Expected name '{expected_name}' in details, got {details}"
    )


@then('the product details should be displayed in the form fields')
def step_form_fields_populated(context):
    """Verify the read form fields are populated."""
    for field_id in ("name", "price", "category"):
        value = _wait(context).until(
            lambda d, fid=field_id: d.find_element(By.ID, fid).get_attribute("value")
        )
        assert value, f"Field {field_id} is empty"


@then('the product should be updated successfully')
def step_updated_successfully(context):
    """Verify the updated-product card shows the new name."""
    _wait(context).until(
        lambda d: "hidden"
        not in (d.find_element(By.ID, "updated-product").get_attribute("class") or "")
    )
    if context.updated_name:
        details = _details_lookup(context.driver, "updated-product-details")
        assert details.get("name") == context.updated_name, (
            f"Expected updated name '{context.updated_name}', got {details}"
        )


@then('I should see the updated product details')
def step_see_updated_details(context):
    """Verify the updated/purchased details card is visible and non-empty."""
    url = context.driver.current_url
    if "/update" in url:
        card_id, details_id = "updated-product", "updated-product-details"
    else:
        card_id, details_id = "purchased-product", "purchased-product-details"
    _wait(context).until(
        lambda d: "hidden"
        not in (d.find_element(By.ID, card_id).get_attribute("class") or "")
    )
    details = _details_lookup(context.driver, details_id)
    assert details, f"Details container {details_id} is empty"


@then('the product should be deleted successfully')
def step_deleted_successfully(context):
    """Verify the delete page shows a success message."""
    _wait(context).until(lambda d: "success" in _message_class(d))


@then('I should see a success message indicating the product was removed')
def step_success_removed(context):
    """Verify the delete success message text mentions deletion/removal."""
    def _check(driver):
        cls = _message_class(driver)
        text = _message_text(driver).lower()
        return "success" in cls and ("deleted" in text or "removed" in text)

    _wait(context).until(_check)


@then('the stock quantity should be decremented to {expected:d}')
def step_stock_decremented(context, expected):
    """Verify the purchased product details show the expected stock value."""
    _wait(context).until(
        lambda d: "hidden"
        not in (d.find_element(By.ID, "purchased-product").get_attribute("class") or "")
    )
    details = _details_lookup(context.driver, "purchased-product-details")
    actual = details.get("stock")
    assert actual == str(expected), f"Expected stock {expected}, got {actual}"


@then('I should see all products displayed in the results area')
def step_see_all_products(context):
    """Verify the list page table shows the expected number of seeded rows."""
    _wait(context).until(
        lambda d: not d.find_element(By.ID, "products-table").get_attribute("hidden")
    )
    rows = context.driver.find_elements(By.CSS_SELECTOR, "#products-tbody tr")
    expected = context.expected_count or len(context.products)
    assert len(rows) == expected, f"Expected {expected} rows, got {len(rows)}"


@then('I should see only products in the "{category}" category displayed in the results area')
def step_see_category_only(context, category):
    """Verify the list page table only shows products of the given category."""
    _wait(context).until(
        lambda d: not d.find_element(By.ID, "products-table").get_attribute("hidden")
    )
    rows = context.driver.find_elements(By.CSS_SELECTOR, "#products-tbody tr")
    assert rows, "Expected at least one product in results"
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        category_cell = cells[2].text.strip()
        assert category_cell.lower() == category.lower(), (
            f"Row category '{category_cell}' does not match '{category}'"
        )


@then('I should see a message indicating no products were found')
def step_no_products_message(context):
    """Verify the list page reports no products are present."""
    _wait(context).until(
        lambda d: "no products" in _message_text(d).lower()
        or "no products"
        in (d.find_element(By.ID, "empty-state").text or "").lower()
    )
