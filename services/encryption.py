from cryptography.fernet import Fernet
import os
import base64

class EncryptionService:
    def __init__(self):
        # In production, this MUST come from a secure env var
        # For this MVP/Demo, we guarantee a key exists or generate one
        # To persist across restarts without a .env manager, we might need to rely on a fixed salt or file.
        # But for security compliance (PVD), we simulate proper key management.
        
        self.key = os.environ.get("MASTER_KEY")
        if not self.key:
             # Generates a valid url-safe base64-encoded 32-byte key
             # In a real deployed app, logging this is bad, but for local dev setup we need to see it to set it
             self.key = Fernet.generate_key().decode()
             print(f"⚠️ SECURITY WARNING: Generated temporary MASTER_KEY: {self.key}")
             print("Please set this in your environment variables to persist encryption.")
        
        self.cipher_suite = Fernet(self.key.encode() if isinstance(self.key, str) else self.key)

    def encrypt(self, plain_text: str) -> str:
        if not plain_text: return ""
        return self.cipher_suite.encrypt(plain_text.encode()).decode()

    def decrypt(self, cipher_text: str) -> str:
        if not cipher_text: return ""
        try:
            return self.cipher_suite.decrypt(cipher_text.encode()).decode()
        except Exception:
            return ""

# Singleton instance
encryption = EncryptionService()
