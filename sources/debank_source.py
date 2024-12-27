from typing import List
from decimal import Decimal
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models.position import Position
from interfaces.data_source import DataSource
from services.web_driver_service import WebDriverService
from config.settings import Settings
import time

class DebankSource(DataSource):
    def __init__(self, settings: Settings, web_driver_service: WebDriverService):
        self.settings = settings
        self.web_driver_service = web_driver_service
        self.urls_and_platforms = settings.debank_sources

    def fetch_positions(self) -> List[Position]:
        all_positions = []
        
        for url, platform in self.urls_and_platforms:
            positions = self._scrape_profile(url, platform)
            if positions:
                all_positions.extend(positions)
                
        return all_positions

    def _scrape_profile(self, url: str, platform: str) -> List[Position]:
        driver = self.web_driver_service.get_driver()
        positions = []

        try:
            driver.get(url)
            wait = WebDriverWait(driver, 7)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ProjectCell_assetsItemWorth__EMwu2")))
            time.sleep(3)

            worth_elements = driver.find_elements(By.CLASS_NAME, "ProjectCell_assetsItemWorth__EMwu2")
            name_elements = driver.find_elements(By.CLASS_NAME, "ProjectCell_assetsItemNameText__l9fan")

            for name, worth in zip(name_elements, worth_elements):
                worth_value = self._clean_worth_value(worth.text.strip())
                
                if worth_value >= Decimal('5'):
                    positions.append(Position(
                        name=name.text.strip(),
                        worth=worth_value,
                        platform=platform
                    ))

            return positions

        finally:
            driver.quit()

    @staticmethod
    def _clean_worth_value(worth_text: str) -> Decimal:
        try:
            cleaned_value = worth_text.replace('$', '').replace(',', '')
            return Decimal(cleaned_value)
        except (ValueError, TypeError):
            return Decimal('0')