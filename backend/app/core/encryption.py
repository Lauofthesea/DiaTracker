"""
Data encryption utilities for sensitive fields.
Uses AES-256 encryption for HIPAA compliance.
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
from typing import Optional

from app.core.config import settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""
    
    def __init__(self):
        """Initialize encryption service with key derivation."""
        # Derive a proper 32-byte key from the encryption key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'ml_diabetes_tracker_salt',  # In production, use a secure random salt
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(
            kdf.derive(settings.ENCRYPTION_KEY.encode())
        )
        self.cipher = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string using AES-256.
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return plaintext
        
        encrypted_bytes = self.cipher.encrypt(plaintext.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string.
        
        Args:
            ciphertext: The encrypted string to decrypt
            
        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ciphertext
        
        decrypted_bytes = self.cipher.decrypt(ciphertext.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    
    def encrypt_optional(self, plaintext: Optional[str]) -> Optional[str]:
        """Encrypt optional string field."""
        return self.encrypt(plaintext) if plaintext else None
    
    def decrypt_optional(self, ciphertext: Optional[str]) -> Optional[str]:
        """Decrypt optional string field."""
        return self.decrypt(ciphertext) if ciphertext else None


# Global encryption service instance
encryption_service = EncryptionService()
