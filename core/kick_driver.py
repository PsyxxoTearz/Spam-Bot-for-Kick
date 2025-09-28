import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class KickDriver:
    def __init__(self, profile_dir, headless=False):
        self.profile_dir = profile_dir
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={self.profile_dir}")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
        
        self.driver = uc.Chrome(options=options, use_subprocess=False)
        return self.driver
    
    def accept_popups(self):
        try:
            time.sleep(2)
            selectors = [
                "button[title*='accept']", "button[title*='Accept']",
                "button:contains('Accept')", "button:contains('Принять')",
                "button:contains('Согласиться')", "button:contains('ОК')",
                ".cky-btn-accept", "#acceptButton", ".accept-cookies"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        buttons = self.driver.find_elements(By.XPATH, selector)
                    else:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(1)
                            break
                except:
                    continue
        except:
            pass
    
    def login_account(self, streamer_url):
        self.driver.get(streamer_url)
        time.sleep(5)
        self.accept_popups()
        return True
    
    def send_message(self, message):
        try:
            chat_selectors = [
                "//div[@data-testid='chat-input']",
                "textarea", "input[placeholder*='chat']",
                "div[contenteditable='true']", "[role='textbox']"
            ]
            
            for selector in chat_selectors:
                try:
                    if selector.startswith("//"):
                        chat_input = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        chat_input = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    chat_input.click()
                    chat_input.send_keys(message)
                    chat_input.send_keys("\n")
                    return True
                except:
                    continue
            return False
        except:
            return False
    
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass