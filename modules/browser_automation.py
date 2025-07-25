"""Browser automation helpers using Selenium."""

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
except Exception as e:  # pragma: no cover - optional dependency
    webdriver = None
    By = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

MODULE_NAME = "browser_automation"
_driver = None
_webview_callback = lambda url: None

def set_webview_callback(func) -> None:
    """Register a callback for GUI web view updates."""
    global _webview_callback
    _webview_callback = func

__all__ = [
    "start_browser",
    "open_url",
    "click_selector",
    "quit_browser",
    "set_webview_callback",
]


def start_browser(headless: bool = True):
    """Launch a Selenium Chrome browser."""
    global _driver
    if webdriver is None:
        return f"selenium not available: {_IMPORT_ERROR}"
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument('--headless')
    _driver = webdriver.Chrome(options=opts)
    return "browser started"


def open_url(url: str) -> str:
    if not _driver:
        return "browser not started"
    _driver.get(url)
    try:
        _webview_callback(url)
    except Exception:
        pass
    return f"opened {url}"


def click_selector(selector: str) -> str:
    if not _driver:
        return "browser not started"
    el = _driver.find_element(By.CSS_SELECTOR, selector)
    el.click()
    return "clicked"


def quit_browser():
    global _driver
    if _driver:
        _driver.quit()
        _driver = None


def get_description() -> str:
    return "Automates a web browser using Selenium WebDriver."
