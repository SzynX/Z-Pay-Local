import base64
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import ecdsa


class CryptoEngine:
    """
    A Z-Pay Local kriptográfiai motorja.
    Felelős a biztonságos kulcskezelésért és az aláírásokért.
    """

    @staticmethod
    def generate_keypair():
        """
        Létrehoz egy új SECP256k1 kulcspárt.
        Ez ugyanaz a görbe, amelyet a Bitcoin és az Ethereum is használ.
        Visszatérési érték: (privát_kulcs_hex, publikus_kulcs_hex)
        """
        # Privát kulcs generálása
        priv_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        # Publikus kulcs származtatása a privátból
        pub_key = priv_key.get_verifying_key()

        return priv_key.to_string().hex(), pub_key.to_string().hex()

    @staticmethod
    def _derive_key(password: str, salt: bytes):
        """
        Belső függvény: PBKDF2 algoritmus segítségével egy biztonságos
        titkosító kulcsot generál a felhasználó jelszavából.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Magas iterációszám a brute-force ellen
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def encrypt_private_key(priv_hex: str, password: str):
        """
        Titkosítja a privát kulcsot a megadott jelszóval (AES-256/Fernet).
        A mentett adat tartalmazza a sót (salt) is a későbbi visszafejtéshez.
        """
        salt = os.urandom(16)  # Véletlenszerű só generálása
        key = CryptoEngine._derive_key(password, salt)
        f = Fernet(key)

        encrypted_data = f.encrypt(priv_hex.encode())
        # Összefűzzük a sót és a titkosított adatot, majd base64-be kódoljuk a tároláshoz
        return base64.b64encode(salt + encrypted_data).decode()

    @staticmethod
    def decrypt_private_key(encrypted_blob: str, password: str):
        """
        Visszafejti a titkosított privát kulcsot a jelszó segítségével.
        Ha a jelszó hibás, None-t ad vissza.
        """
        try:
            # Base64 visszaalakítása byte-okká
            blob = base64.b64decode(encrypted_blob.encode())
            # Az első 16 byte a só, a maradék a titkosított adat
            salt, data = blob[:16], blob[16:]

            key = CryptoEngine._derive_key(password, salt)
            f = Fernet(key)

            return f.decrypt(data).decode()
        except Exception:
            # Bármilyen hiba (rossz jelszó, sérült adat) esetén meghiúsul
            return None

    @staticmethod
    def sign_transaction(priv_hex: str, message: str):
        """
        Digitális aláírást készít egy üzenetre (tranzakció adatai)
        a privát kulcs használatával.
        """
        priv_key = ecdsa.SigningKey.from_string(
            bytes.fromhex(priv_hex),
            curve=ecdsa.SECP256k1
        )
        # Aláírjuk az üzenetet (pl. "küldő-fogadó-összeg")
        signature = priv_key.sign(message.encode())
        return signature.hex()

    @staticmethod
    def verify_signature(pub_hex: str, message: str, signature: str):
        """
        Ellenőrzi, hogy egy adott aláírás érvényes-e az üzenethez
        a küldő publikus kulcsa alapján. (Zero Knowledge alapelv)
        """
        try:
            pub_key = ecdsa.VerifyingKey.from_string(
                bytes.fromhex(pub_hex),
                curve=ecdsa.SECP256k1
            )
            # Ha az aláírás nem egyezik, ez hibát dob
            return pub_key.verify(bytes.fromhex(signature), message.encode())
        except Exception:
            return False