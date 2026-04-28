"""
Behave environment setup for Selenium WebDriver.

The BDD suite is strictly UI-only: every interaction with the service goes
through the admin web pages via Selenium. No direct REST/API calls are made
from this file or from any step definition.
"""

import os
import shutil
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


WAIT_SECONDS = int(os.getenv("WAIT_SECONDS", "30"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

BROWSER_CANDIDATES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
)
DRIVER_CANDIDATES = (
    "chromedriver",
    "/usr/lib/chromium/chromedriver",
    "/usr/lib/chromium-browser/chromedriver",
    "/usr/bin/chromedriver",
)


def _find_first(candidates):
    for candidate in candidates:
        if os.path.isabs(candidate):
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
        else:
            path = shutil.which(candidate)
            if path:
                return path
    return None


def before_all(context):
    """Start a single Selenium driver for the whole test run."""
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,1024")

    browser_path = os.getenv("CHROME_BIN") or _find_first(BROWSER_CANDIDATES)
    if browser_path:
        chrome_options.binary_location = browser_path

    driver_path = os.getenv("CHROMEDRIVER") or _find_first(DRIVER_CANDIDATES)
    service = Service(executable_path=driver_path) if driver_path else Service()

    context.driver = webdriver.Chrome(  # pylint: disable=not-callable
        service=service, options=chrome_options
    )
    context.driver.implicitly_wait(context.wait_seconds)


def before_scenario(context, scenario):  # pylint: disable=unused-argument
    """Reset shared scenario state and purge all products via the admin UI."""
    context.products = {}
    context.created_payload = None
    context.updated_name = None
    context.expected_count = 0
    context.expected_categories = []

    _purge_all_products_via_ui(context)


def after_all(context):
    """Stop the Selenium driver after the test run."""
    if hasattr(context, "driver"):
        context.driver.quit()


def _purge_all_products_via_ui(context):
    """Delete every product currently in the catalog by driving the admin UI."""
    driver = context.driver
    wait = WebDriverWait(driver, context.wait_seconds)

    driver.get(f"{context.base_url}/admin/products/list")
    wait.until(EC.element_to_be_clickable((By.ID, "list-all-button"))).click()

    try:
        wait.until(
            lambda d: not d.find_element(By.ID, "products-table").get_attribute("hidden")
            or "no products" in d.find_element(By.ID, "message").text.lower()
            or "no products" in d.find_element(By.ID, "empty-state").text.lower()
        )
    except TimeoutException:
        return

    rows = driver.find_elements(By.CSS_SELECTOR, "#products-tbody tr")
    ids = [row.find_elements(By.TAG_NAME, "td")[0].text.strip() for row in rows]

    for product_id in ids:
        if not product_id:
            continue
        driver.get(f"{context.base_url}/admin/products/delete")
        wait.until(EC.presence_of_element_located((By.ID, "delete-product-id"))).clear()
        driver.find_element(By.ID, "delete-product-id").send_keys(product_id)
        driver.find_element(By.ID, "delete-button").click()
        wait.until(
            lambda d: "success" in d.find_element(By.ID, "message").get_attribute("class")
            or "error" in d.find_element(By.ID, "message").get_attribute("class")
        )
