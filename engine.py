import base64
import os
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import ecdsa


class CryptoEngine:
    """
    Z-Pay 2.0 Kriptográfiai Motor.
    A Zero Knowledge elv alapján működik: a rendszer soha nem ismeri a jelszavadat,
    minden művelet (titkosítás, aláírás) lokálisan történik a memóriában.
    """

    @staticmethod
    def generate_keypair():
        """
        Létrehoz egy új SECP256k1 kulcspárt és egy egyedi 0x-címet.
        Visszatérési érték: (privát_hex, 0x_cím, publikus_hex)
        """
        # 1. SECP256k1 privát kulcs generálása (Bitcoin/Ethereum standard)
        priv_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)

        # 2. Publikus kulcs származtatása a privátból
        pub_key = priv_key.get_verifying_key()
        pub_hex = pub_key.to_string().hex()

        # 3. Ethereum-stílusú cím generálása
        # A publikus kulcs SHA256 hash-éből vesszük az első 40 karaktert
        pub_bytes = pub_key.to_string()
        address_hash = hashlib.sha256(pub_bytes).hexdigest()
        address = "0x" + address_hash[:40]

        return priv_key.to_string().hex(), address, pub_hex

    @staticmethod
    def _derive_key(password: str, salt: bytes):
        """
        Belső segédfüggvény: Biztonságos AES kulcsot generál a jelszóból PBKDF2-vel.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Magas iteráció a brute-force támadások ellen
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def encrypt_private_key(priv_hex: str, password: str):
        """
        Titkosítja a privát kulcsot AES-256 (Fernet) használatával.
        A jelszót csak a folyamat idejére használjuk, nem mentjük el.
        """
        salt = os.urandom(16)  # Egyedi só minden egyes fiókhoz
        key = CryptoEngine._derive_key(password, salt)
        f = Fernet(key)

        encrypted_data = f.encrypt(priv_hex.encode())

        # A mentett adat: 16 byte só + titkosított adat
        combined_blob = salt + encrypted_data
        return base64.b64encode(combined_blob).decode()

    @staticmethod
    def decrypt_private_key(encrypted_blob: str, password: str):
        """
        Visszafejti a privát kulcsot a jelszóval.
        Hibás jelszó esetén None-t ad vissza.
        """
        try:
            # Base64-ből byte-okká
            blob = base64.b64decode(encrypted_blob.encode())

            # Só (első 16 byte) és a titkosított tartalom szétválasztása
            salt = blob[:16]
            data = blob[16:]

            # Kulcs újragenerálása a jelszóból és a fájlból kiolvasott sóból
            key = CryptoEngine._derive_key(password, salt)
            f = Fernet(key)

            return f.decrypt(data).decode()
        except Exception:
            # Ha a jelszó rossz, a Fernet dekódolás elbukik
            return None

    @staticmethod
    def sign_transaction(priv_hex: str, message: str):
        """
        Digitális aláírást készít a tranzakció adataira.
        Ez bizonyítja, hogy a tranzakciót a kulcs tulajdonosa indította.
        """
        priv_key = ecdsa.SigningKey.from_string(
            bytes.fromhex(priv_hex),
            curve=ecdsa.SECP256k1
        )
        # Az aláírás egyedi az adott üzenetre nézve
        signature = priv_key.sign(message.encode())
        return signature.hex()

    @staticmethod
    def verify_signature(pub_hex: str, message: str, signature: str):
        """
        Ellenőrzi, hogy az aláírás valóban a publikus kulcshoz tartozó
        privát kulccsal készült-e. (Hálózati validáció)
        """
        try:
            pub_key = ecdsa.VerifyingKey.from_string(
                bytes.fromhex(pub_hex),
                curve=ecdsa.SECP256k1
            )
            return pub_key.verify(bytes.fromhex(signature), message.encode())
        except Exception:
            # Ha az aláírás nem valid vagy módosították az üzenetet
            return False