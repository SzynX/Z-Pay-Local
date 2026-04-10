import base64
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import ecdsa

class CryptoEngine:
    @staticmethod
    def generate_keypair():
        """Új SECP256k1 kulcspár generálása (mint a Bitcoin)."""
        priv_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        pub_key = priv_key.get_verifying_key()
        return priv_key.to_string().hex(), pub_key.to_string().hex()

    @staticmethod
    def _derive_key(password: str, salt: bytes):
        """Jelszóból titkosító kulcs készítése (PBKDF2)."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def encrypt_private_key(priv_hex, password):
        salt = os.urandom(16)
        key = CryptoEngine._derive_key(password, salt)
        f = Fernet(key)
        encrypted_data = f.encrypt(priv_hex.encode())
        return base64.b64encode(salt + encrypted_data).decode()

    @staticmethod
    def decrypt_private_key(encrypted_blob, password):
        try:
            blob = base64.b64decode(encrypted_blob.encode())
            salt, data = blob[:16], blob[16:]
            key = CryptoEngine._derive_key(password, salt)
            f = Fernet(key)
            return f.decrypt(data).decode()
        except:
            return None

    @staticmethod
    def sign_transaction(priv_hex, message):
        priv_key = ecdsa.SigningKey.from_string(bytes.fromhex(priv_hex), curve=ecdsa.SECP256k1)
        return priv_key.sign(message.encode()).hex()

    @staticmethod
    def verify_signature(pub_hex, message, signature):
        try:
            pub_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(pub_hex), curve=ecdsa.SECP256k1)
            return pub_key.verify(bytes.fromhex(signature), message.encode())
        except:
            return False