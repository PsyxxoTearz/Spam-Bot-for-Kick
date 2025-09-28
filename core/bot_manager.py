import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from .kick_driver import KickDriver
import time

class BotManager:
    def __init__(self):
        self.accounts_file = "data/accounts.json"
        self.config_file = "data/config.json"
        self.accounts = self.load_accounts()
        self.config = self.load_config()
    
    def load_accounts(self):
        if os.path.exists(self.accounts_file):
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"streamer": "", "message": "", "profiles_dir": "kick_profiles"}
    
    def save_accounts(self):
        os.makedirs("data", exist_ok=True)
        with open(self.accounts_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, ensure_ascii=False, indent=2)
    
    def save_config(self):
        os.makedirs("data", exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, ensure_ascii=False, indent=2)
    
    def add_account(self, name, password, profile_name):
        account = {
            "name": name,
            "password": password,
            "profile_dir": os.path.join(self.config["profiles_dir"], profile_name)
        }
        self.accounts.append(account)
        self.save_accounts()
    
    def remove_account(self, index):
        if 0 <= index < len(self.accounts):
            self.accounts.pop(index)
            self.save_accounts()
    
    def update_config(self, streamer, message):
        self.config["streamer"] = streamer
        self.config["message"] = message
        self.save_config()
    
    def setup_account(self, account_index):
        if account_index >= len(self.accounts):
            return False, "Аккаунт не найден"
        
        account = self.accounts[account_index]
        driver = KickDriver(account["profile_dir"], False)
        
        try:
            driver.setup_driver()
            driver.login_account("https://kick.com")
            time.sleep(3)
            return True, "Настройка завершена"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"
        finally:
            driver.close()
    
    def send_single_message(self, account_index, headless=False):
        if account_index >= len(self.accounts):
            return False, "Аккаунт не найден"
        
        account = self.accounts[account_index]
        streamer_url = f"https://kick.com/{self.config['streamer']}"
        
        driver = KickDriver(account["profile_dir"], headless)
        
        try:
            driver.setup_driver()
            if driver.login_account(streamer_url):
                time.sleep(3)
                if driver.send_message(self.config["message"]):
                    return True, "Сообщение отправлено"
                else:
                    return False, "Не удалось отправить сообщение"
            else:
                return False, "Ошибка входа"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"
        finally:
            driver.close()
    
    def send_messages_parallel(self, headless=False):
        results = []
        
        def send_wrapper(index):
            success, message = self.send_single_message(index, headless)
            return self.accounts[index]["name"], success, message
        
        with ThreadPoolExecutor(max_workers=len(self.accounts)) as executor:
            futures = [executor.submit(send_wrapper, i) for i in range(len(self.accounts))]
            
            for future in as_completed(futures):
                results.append(future.result())
        
        return results