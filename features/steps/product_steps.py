"""
Product seeding step definitions.

These Given steps establish preconditions for scenarios by driving the admin
UI through Selenium. No direct REST/API calls are made here.
"""

# pylint: disable=not-callable,no-name-in-module
from behave import given
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _wait(context):
    return WebDriverWait(context.driver, context.wait_seconds)


def _create_product_via_ui(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    context,
    name="BDD Product",
    description="A product created by the BDD suite",
    price="9.99",
    category="Default",
    stock=10,
    available=True,
):
    """Drive the Create admin page to add a product and return its real id."""
    driver = context.driver
    wait = _wait(context)

    driver.get(f"{context.base_url}/admin/products/create")
    wait.until(EC.presence_of_element_located((By.ID, "name")))

    fields = {
        "name": str(name),
        "description": str(description),
        "price": str(price),
        "category": str(category),
        "stock": str(stock),
    }
    for field_id, value in fields.items():
        element = driver.find_element(By.ID, field_id)
        element.clear()
        element.send_keys(value)

    available_checkbox = driver.find_element(By.ID, "available")
    if available != available_checkbox.is_selected():
        available_checkbox.click()

    driver.find_element(By.ID, "create-button").click()

    wait.until(
        lambda d: "hidden"
        not in (d.find_element(By.ID, "created-product").get_attribute("class") or "")
    )

    details = driver.find_element(By.ID, "created-product-details")
    dt_elements = details.find_elements(By.TAG_NAME, "dt")
    dd_elements = details.find_elements(By.TAG_NAME, "dd")
    for label, value in zip(dt_elements, dd_elements):
        if label.text.strip().lower() == "id":
            return value.text.strip()

    raise RuntimeError("Could not parse created product id from the admin UI")


def _set_product_unavailable_via_ui(context, real_id):
    """Drive the Update admin page to mark a product unavailable with stock 0.

    The driver is returned to whatever URL it was on before, so this helper is
    transparent to the surrounding scenario.
    """
    driver = context.driver
    wait = _wait(context)
    original_url = driver.current_url

    driver.get(f"{context.base_url}/admin/products/update")
    wait.until(EC.presence_of_element_located((By.ID, "retrieve-product-id")))

    retrieve_field = driver.find_element(By.ID, "retrieve-product-id")
    retrieve_field.clear()
    retrieve_field.send_keys(str(real_id))
    driver.find_element(By.ID, "retrieve-button").click()

    wait.until(
        lambda d: d.find_element(By.ID, "update-button").get_attribute("disabled") is None
    )

    stock_field = driver.find_element(By.ID, "stock")
    stock_field.clear()
    stock_field.send_keys("0")
    stock_field.send_keys("\t")

    available_checkbox = driver.find_element(By.ID, "available")
    if available_checkbox.is_selected():
        available_checkbox.click()

    driver.find_element(By.ID, "update-button").click()

    wait.until(
        lambda d: "hidden"
        not in (d.find_element(By.ID, "updated-product").get_attribute("class") or "")
    )

    if original_url and original_url != driver.current_url:
        driver.get(original_url)


@given('a product with id "{alias}" exists in the database')
def step_product_exists(context, alias):
    """Seed exactly one product via the Create admin page."""
    real_id = _create_product_via_ui(context)
    context.products[alias] = real_id


@given('a product with id "{alias}" exists and has a stock quantity of {stock:d}')
def step_product_with_stock(context, alias, stock):
    """Seed a product with a specific stock level via the Create admin page."""
    real_id = _create_product_via_ui(
        context,
        name="BDD Purchasable Product",
        category="Purchasable",
        stock=stock,
        available=stock > 0,
    )
    context.products[alias] = real_id


@given('product "{alias}" is unavailable or has a stock quantity of 0')
def step_make_unavailable(context, alias):
    """Force the seeded product to be unavailable via the Update admin page."""
    real_id = context.products[alias]
    _set_product_unavailable_via_ui(context, real_id)


@given('multiple products exist in the database')
def step_multiple_products(context):
    """Seed three products via the Create admin page."""
    seeds = [
        {"name": "BDD Alpha", "category": "Alpha"},
        {"name": "BDD Bravo", "category": "Bravo"},
        {"name": "BDD Charlie", "category": "Charlie"},
    ]
    for index, seed in enumerate(seeds, start=1):
        real_id = _create_product_via_ui(
            context,
            name=seed["name"],
            category=seed["category"],
        )
        context.products[f"prod_{index}"] = real_id
    context.expected_count = len(seeds)


@given('no products exist in the database')
def step_no_products(context):
    """Cleanup is performed in before_scenario; this is just an explicit assertion."""
    assert context.products == {}, (
        f"Expected no seeded products, but context.products={context.products}"
    )


@given('products exist in categories "{cat1}" and "{cat2}"')
def step_products_in_categories(context, cat1, cat2):
    """Seed two products in each of two categories via the Create admin page."""
    for category in (cat1, cat2):
        for index in range(1, 3):
            real_id = _create_product_via_ui(
                context,
                name=f"{category} Item {index}",
                category=category,
            )
            context.products[f"{category}_{index}"] = real_id
    context.expected_categories = [cat1, cat2]
    context.expected_count = 4
