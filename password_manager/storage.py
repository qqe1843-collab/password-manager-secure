import json
import os
from datetime import datetime
from password_manager.crypto import PasswordCrypto

class PasswordStorage:
    """Класс для управления хранилищем паролей"""
    
    def __init__(self, filename: str = 'passwords.json'):
        self.filename = filename
        self.passwords = {}
        self.load_passwords()
    
    def load_passwords(self):
        """Загружает пароли из файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.passwords = json.load(f)
            except:
                self.passwords = {}
        else:
            self.passwords = {}
    
    def save_passwords(self):
        """Сохраняет пароли в файл"""
        with open(self.filename, 'w') as f:
            json.dump(self.passwords, f, indent=2)
    
    def add_password(self, site: str, username: str, password: str, notes: str, master_password: str) -> bool:
        """
        Добавляет новый пароль
        """
        try:
            encrypted_password = PasswordCrypto.encrypt_password(password, master_password)
            
            entry_id = f"{site}_{username}_{datetime.now().timestamp()}"
            self.passwords[entry_id] = {
                'site': site,
                'username': username,
                'password': encrypted_password,
                'notes': notes,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            self.save_passwords()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении пароля: {str(e)}")
            return False
    
    def get_password(self, entry_id: str, master_password: str) -> dict:
        """
        Получает расшифрованный пароль
        """
        try:
            entry = self.passwords[entry_id]
            decrypted_password = PasswordCrypto.decrypt_password(entry['password'], master_password)
            
            return {
                'id': entry_id,
                'site': entry['site'],
                'username': entry['username'],
                'password': decrypted_password,
                'notes': entry['notes'],
                'created_at': entry['created_at'],
                'updated_at': entry['updated_at']
            }
        except Exception as e:
            print(f"Ошибка при получении пароля: {str(e)}")
            return None
    
    def get_all_passwords(self, master_password: str) -> list:
        """
        Получает все пароли (расшифрованные)
        """
        result = []
        for entry_id, entry in self.passwords.items():
            try:
                decrypted_password = PasswordCrypto.decrypt_password(entry['password'], master_password)
                result.append({
                    'id': entry_id,
                    'site': entry['site'],
                    'username': entry['username'],
                    'password': decrypted_password,
                    'notes': entry['notes'],
                    'created_at': entry['created_at'],
                    'updated_at': entry['updated_at']
                })
            except:
                pass
        
        return result
    
    def update_password(self, entry_id: str, site: str, username: str, password: str, notes: str, master_password: str) -> bool:
        """
        Обновляет существующий пароль
        """
        try:
            if entry_id not in self.passwords:
                return False
            
            encrypted_password = PasswordCrypto.encrypt_password(password, master_password)
            
            self.passwords[entry_id] = {
                'site': site,
                'username': username,
                'password': encrypted_password,
                'notes': notes,
                'created_at': self.passwords[entry_id]['created_at'],
                'updated_at': datetime.now().isoformat()
            }
            
            self.save_passwords()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении пароля: {str(e)}")
            return False
    
    def delete_password(self, entry_id: str) -> bool:
        """
        Удаляет пароль
        """
        try:
            if entry_id in self.passwords:
                del self.passwords[entry_id]
                self.save_passwords()
                return True
            return False
        except Exception as e:
            print(f"Ошибка при удалении пароля: {str(e)}")
            return False
    
    def search_passwords(self, query: str, master_password: str) -> list:
        """
        Ищет пароли по сайту или пользователю
        """
        results = []
        query_lower = query.lower()
        
        for entry_id, entry in self.passwords.items():
            if query_lower in entry['site'].lower() or query_lower in entry['username'].lower():
                try:
                    decrypted_password = PasswordCrypto.decrypt_password(entry['password'], master_password)
                    results.append({
                        'id': entry_id,
                        'site': entry['site'],
                        'username': entry['username'],
                        'password': decrypted_password,
                        'notes': entry['notes'],
                        'created_at': entry['created_at'],
                        'updated_at': entry['updated_at']
                    })
                except:
                    pass
        
        return results
