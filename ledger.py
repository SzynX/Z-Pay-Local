import json
import os
import time
from datetime import datetime

# A közös adatbázis fájl neve, amely a "hálózatot" szimulálja
LEDGER_FILE = "global_ledger.json"


class Ledger:
    """
    A Ledger osztály felelős a tranzakciók tárolásáért, az egyenlegek
    kiszámításáért és a tranzakciók hitelesítéséért.
    """

    def __init__(self):
        """Inicializáláskor ellenőrzi, létezik-e a főkönyv. Ha nem, létrehozza."""
        if not os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE, "w") as f:
                json.dump([], f)

    def get_all_transactions(self):
        """Beolvassa az összes tranzakciót a fájlból."""
        try:
            if not os.path.exists(LEDGER_FILE):
                return []
            with open(LEDGER_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return []

    def get_balance(self, address):
        """
        Kiszámolja egy adott cím egyenlegét.
        Minden új tárca 1000 ZCOIN "ajándék" egyenleggel indul a gyakorláshoz.
        """
        balance = 1000.0  # Kezdőegyenleg (Genesis)
        transactions = self.get_all_transactions()

        for tx in transactions:
            if tx['sender'] == address:
                balance -= tx['amount']
            if tx['receiver'] == address:
                balance += tx['amount']

        return balance

    def get_history(self, address):
        """
        Visszaadja a megadott címhez tartozó összes tranzakciót.
        Időrendben csökkenő sorrendbe rendezi (legújabb elöl).
        """
        all_tx = self.get_all_transactions()
        # Szűrés: csak azok a tranzakciók, ahol a cím küldő vagy fogadó
        history = [tx for tx in all_tx if tx['sender'] == address or tx['receiver'] == address]

        # Rendezés timestamp (időbélyeg) szerint csökkenő sorrendbe
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)

    def add_transaction(self, sender_pub, receiver_pub, amount, signature):
        """
        Új tranzakció hozzáadása a hálózathoz.
        Folyamat:
        1. Aláírás ellenőrzése
        2. Egyenleg ellenőrzése
        3. Mentés
        """
        from engine import CryptoEngine  # Lokális import a körkörös hivatkozás elkerülésére

        # 1. Aláírás ellenőrzése (Matematikai bizonyíték, hogy a küldő indította)
        # Az üzenet formátuma ugyanaz kell legyen, mint amit a küldő aláírt
        msg = f"{sender_pub}-{receiver_pub}-{amount}"
        if not CryptoEngine.verify_signature(sender_pub, msg, signature):
            return False, "Hiba: Érvénytelen digitális aláírás!"

        # 2. Összeg érvényességének ellenőrzése
        if amount <= 0:
            return False, "Hiba: Az összegnek nagyobbnak kell lennie nullánál!"

        # 3. Saját magának nem utalhat
        if sender_pub == receiver_pub:
            return False, "Hiba: Önmagának nem küldhet pénzt!"

        # 4. Fedezet ellenőrzése
        current_balance = self.get_balance(sender_pub)
        if current_balance < amount:
            return False, f"Hiba: Nincs elég fedezet! (Aktuális: {current_balance})"

        # 5. Tranzakció összeállítása
        tx = {
            "sender": sender_pub,
            "receiver": receiver_pub,
            "amount": amount,
            "signature": signature,
            "timestamp": time.time(),
            "date_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 6. Mentés a fájlba
        try:
            all_tx = self.get_all_transactions()
            all_tx.append(tx)

            with open(LEDGER_FILE, "w") as f:
                json.dump(all_tx, f, indent=4)

            return True, "Sikeres tranzakció elküldve a hálózatra!"
        except Exception as e:
            return False, f"Rendszerhiba a mentés során: {str(e)}"