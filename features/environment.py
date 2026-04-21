"""
Behave environment setup for Selenium WebDriver
"""

import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def before_all(context):
    """Set up Selenium before the test run."""
    context.base_url = os.getenv("BASE_URL", "http://localhost:8080")

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,1024")

    browser_path = None
    for browser_name in ["chromium", "chromium-browser", "google-chrome"]:
        path = shutil.which(browser_name)
        if path:
            browser_path = path
            break

    if browser_path:
        chrome_options.binary_location = browser_path

    chromedriver_path = shutil.which("chromedriver")
    if not chromedriver_path:
        raise RuntimeError("chromedriver not found. Please install chromium-driver.")

    service = Service(chromedriver_path)
    context.driver = webdriver.Chrome(service=service, options=chrome_options)
    context.driver.implicitly_wait(5)


def after_all(context):
    """Clean up Selenium after the test run."""
    if hasattr(context, "driver"):
        context.driver.quit()
