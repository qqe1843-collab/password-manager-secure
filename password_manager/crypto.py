import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64

class PasswordCrypto:
    """Класс для шифрования и дешифрования паролей"""
    
    SALT_LENGTH = 16
    ITERATIONS = 100000
    
    @staticmethod
    def derive_key(master_password: str, salt: bytes = None) -> tuple:
        """
        Генерирует ключ шифрования из главного пароля
        Возвращает (ключ, соль)
        """
        if salt is None:
            salt = os.urandom(PasswordCrypto.SALT_LENGTH)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=PasswordCrypto.ITERATIONS,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key, salt
    
    @staticmethod
    def encrypt_password(password: str, master_password: str, salt: bytes = None) -> str:
        """
        Шифрует пароль
        Возвращает зашифрованные данные в формате: salt|encrypted_data
        """
        key, salt = PasswordCrypto.derive_key(master_password, salt)
        cipher = Fernet(key)
        encrypted = cipher.encrypt(password.encode())
        
        # Кодируем соль и зашифрованные данные в base64
        salt_b64 = base64.b64encode(salt).decode()
        encrypted_b64 = encrypted.decode()
        
        return f"{salt_b64}|{encrypted_b64}"
    
    @staticmethod
    def decrypt_password(encrypted_data: str, master_password: str) -> str:
        """
        Дешифрует пароль
        encrypted_data должен быть в формате: salt|encrypted_data
        """
        try:
            salt_b64, encrypted_b64 = encrypted_data.split('|')
            salt = base64.b64decode(salt_b64)
            
            key, _ = PasswordCrypto.derive_key(master_password, salt)
            cipher = Fernet(key)
            decrypted = cipher.decrypt(encrypted_b64.encode())
            
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Ошибка при расшифровке: {str(e)}")