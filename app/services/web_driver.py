from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class WebDriverService:
    """Service for managing Selenium WebDriver instances."""
    
    def __init__(self):
        """Initialize WebDriver service with default configurations."""
        self.chrome_options = self._configure_chrome_options()
        self.service = Service(ChromeDriverManager().install())

    def _configure_chrome_options(self):
        """Configure Chrome WebDriver options for headless operation.
        
        Returns:
            Options: Configured Chrome options
        """
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        return options

    @contextmanager
    def get_driver(self):
        """Create and manage a WebDriver instance using context manager.
        
        Yields:
            webdriver.Chrome: Configured Chrome WebDriver instance
        
        Example:
            with web_driver_service.get_driver() as driver:
                driver.get("https://example.com")
        """
        driver = None
        try:
            driver = webdriver.Chrome(
                service=self.service,
                options=self.chrome_options
            )
            driver.implicitly_wait(10)
            logger.info("WebDriver instance created successfully")
            yield driver
        except Exception as e:
            logger.error(f"Error creating WebDriver instance: {str(e)}")
            raise
        finally:
            if driver:
                try:
                    driver.quit()
                    logger.info("WebDriver instance closed successfully")
                except Exception as e:
                    logger.error(f"Error closing WebDriver instance: {str(e)}")

    def update_user_agent(self, user_agent):
        """Update the user agent string for the Chrome options.
        
        Args:
            user_agent (str): New user agent string to use
        """
        self.chrome_options.add_argument(f'--user-agent={user_agent}')

    def add_chrome_option(self, argument):
        """Add a custom Chrome option argument.
        
        Args:
            argument (str): Chrome option argument to add
        """
        self.chrome_options.add_argument(argument)