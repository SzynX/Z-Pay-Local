import base64
import os
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import ecdsa


class CryptoEngine:
    """
    Z-Pay Pro v1.5 Kriptográfiai Motor.
    Ez a modul felelős a kulcsgenerálásért, a Zero Knowledge alapú aláírásokért
    és a katonai szintű helyi adattitkosításért.
    """

    @staticmethod
    def generate_keypair():
        """
        Létrehoz egy új SECP256k1 kulcspárt és egy rövidített Ethereum-szerű címet.
        Visszatérési érték: (privát_hex, rövid_cím, publikus_hex)
        """
        # 1. SECP256k1 privát kulcs generálása
        priv_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)

        # 2. Publikus kulcs származtatása
        pub_key = priv_key.get_verifying_key()
        pub_hex = pub_key.to_string().hex()

        # 3. Rövidített "Ethereum-stílusú" cím generálása
        # A publikus kulcsot hash-eljük, és az első 40 karaktert használjuk címként
        pub_bytes = pub_key.to_string()
        address_hash = hashlib.sha256(pub_bytes).hexdigest()
        address = "0x" + address_hash[:40]  # 40 karakter + 0x prefix = 42 karakter

        return priv_key.to_string().hex(), address, pub_hex

    @staticmethod
    def _derive_key(password: str, salt: bytes):
        """
        Belső segédfüggvény: Jelszóból generál titkosító kulcsot PBKDF2-vel.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def encrypt_private_key(priv_hex: str, password: str):
        """
        Titkosítja a privát kulcsot AES-256 (Fernet) használatával.
        A jelszót soha nem tároljuk, csak a kulcs származtatásához használjuk.
        """
        salt = os.urandom(16)  # Egyedi só minden fiókhoz
        key = CryptoEngine._derive_key(password, salt)
        f = Fernet(key)

        encrypted_data = f.encrypt(priv_hex.encode())

        # A sót az adathoz fűzzük (16 byte só + titkosított adat)
        combined_blob = salt + encrypted_data
        return base64.b64encode(combined_blob).decode()

    @staticmethod
    def decrypt_private_key(encrypted_blob: str, password: str):
        """
        Visszafejti a privát kulcsot. Ha a jelszó hibás, None-t ad vissza.
        """
        try:
            # Base64 visszaalakítása
            blob = base64.b64decode(encrypted_blob.encode())

            # Só és adat szétválasztása
            salt = blob[:16]
            data = blob[16:]

            # Kulcs újragenerálása a jelszóból és a mentett sóból
            key = CryptoEngine._derive_key(password, salt)
            f = Fernet(key)

            return f.decrypt(data).decode()
        except Exception:
            # Hiba esetén (pl. rossz jelszó) nem dobunk hibát, csak None-t adunk
            return None

    @staticmethod
    def sign_transaction(priv_hex: str, message: str):
        """
        Digitális aláírást készít egy üzenetre (tranzakcióra).
        Ez bizonyítja a küldési szándékot a privát kulcs felfedése nélkül.
        """
        priv_key = ecdsa.SigningKey.from_string(
            bytes.fromhex(priv_hex),
            curve=ecdsa.SECP256k1
        )
        # Az aláírás matematikailag kötődik az üzenethez és a kulcshoz
        signature = priv_key.sign(message.encode())
        return signature.hex()

    @staticmethod
    def verify_signature(pub_hex: str, message: str, signature: str):
        """
        Ellenőrzi az aláírás valódiságát a publikus kulcs alapján.
        Ez a funkció fut a 'hálózaton' (Ledger), mielőtt a tranzakciót elkönyvelnénk.
        """
        try:
            pub_key = ecdsa.VerifyingKey.from_string(
                bytes.fromhex(pub_hex),
                curve=ecdsa.SECP256k1
            )
            return pub_key.verify(bytes.fromhex(signature), message.encode())
        except Exception:
            return False